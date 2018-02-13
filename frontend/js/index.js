import '../scss/main.scss';
import * as d3 from 'd3';

function partitionData(data) {
  const obs = data.slice(0, 24);
  const pred = data.slice(24);
  pred.unshift(obs[obs.length - 1]);
  return [obs, pred];
}

(global => {
  const data = global.generationData;
  const chart = d3.select('#chart');
  const width = +chart.attr('width');
  const height = +chart.attr('height');

  const x = d3.scaleLinear().domain([0, data.length]).range([30, width - 30]);
  const y = d3.scaleLinear().domain([0, 1]).range([height, 0]);

  const yAxis = d3.axisLeft(y);
  chart.append('svg:g')
    .attr('class', 'axis axis--y')
    .call(yAxis);

  const observed = d3.line().x((d, i) => x(i)).y(d => y(d)).curve(d3.curveLinear);
  const predicted = d3.line().x((d, i) => x(i + 23) + 5).y(d => y(d)).curve(d3.curveLinear);

  const [obs, pred] = partitionData(data);

  chart.append('svg:path').attr('class', 'line').attr('d', observed(obs));
  chart.append('svg:path').attr('class', 'line line--predicted').attr('d', predicted(pred));

  // Labels, placed at arbitrarily chosen hours along the X axis.
  // Label is placed either above or below the plotted line,
  // depending on where there's more place.

  const labelNames = ['24h-ago', 'now', 'in-6h'];
  const labelPositions = [2, 20, 26].map((hour, i) => {
    const jitter = 125 - Math.floor(Math.random() * 50);
    return {
      hour,
      name: labelNames[i],
      x: x(hour),
      y: data[hour] < 0.5 ? jitter : height - jitter
    };
  });

  labelPositions.forEach(({x, y, name}, i) => {
    const label = chart.select(`[data-locator="${name}"]`);
    const labelDim = +label.attr('width');
    label.attr('x', x - labelDim/2).attr('y', y - labelDim/2);
  });

  // TODO: draw connecting lines

})(window);
