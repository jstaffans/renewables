import '../scss/main.scss';
import * as d3 from 'd3';

// Partitions data into observed and predicted parts.
// They are to be styled differently.
function partitionData(data) {
  const obs = data.slice(0, 24);
  const pred = data.slice(24);
  pred.unshift(obs[obs.length - 1]);
  return [obs, pred];
}

function moveLabel(label, x, y) {
  const labelDim = +label.attr('width');
  label.attr('x', x - labelDim/2).attr('y', y - labelDim/2);
}

(global => {
  const data = global.generationData;
  const chart = d3.select('#chart');
  const width = +chart.attr('width');
  const height = +chart.attr('height');

  const plotX = d3.scaleLinear().domain([0, data.length]).range([60, width - 30]);
  const plotY = d3.scaleLinear().domain([0, 1]).range([height, 0]);

  const yAxis = d3.axisLeft(plotY).ticks(0).tickSizeOuter(0);
  chart.append('svg:g')
    .attr('class', 'chart__axis chart__axis--y')
    .attr('transform', 'translate(30, 28) scale(1.0 0.88)')
    .call(yAxis);

  chart.append('svg:text')
    .attr('class', 'chart__axis-label chart__axis-label--100')
    .attr('y', 20)
    .attr('x', 6)
    .text('100 %');

  chart.append('svg:text')
    .attr('class', 'chart__axis-label chart__axis-label--0')
    .attr('y', height)
    .attr('x', 10)
    .text('0 %');

  chart.selectAll('.tick').remove();

  const [obs, pred] = partitionData(data);
  const observed = d3.line().x((d, i) => plotX(i)).y(d => plotY(d)).curve(d3.curveLinear)(obs);
  const predicted = d3.line().x((d, i) => plotX(i + 23) + 5).y(d => plotY(d)).curve(d3.curveLinear)(pred);

  chart.append('svg:path').attr('class', 'chart__line chart__line--mask').attr('d', observed);
  chart.append('svg:path').attr('class', 'chart__line chart__line--mask').attr('d', predicted);
  chart.append('svg:path').attr('class', 'chart__line').attr('d', observed);
  chart.append('svg:path').attr('class', 'chart__line chart__line--predicted').attr('d', predicted);

  // Labels, placed at arbitrarily chosen hours along the X axis.
  // Label is placed either above or below the plotted line,
  // depending on where there's more place.

  // The label SVG:s are part of the markup.

  const labelNames = ['24h-ago', 'now', 'in-6h'];
  const measurementPoints = [0, 23, 29];
  const labelPositions = [2, 22, 26].map((hour, i) => {
    const jitter = 125 - Math.floor(Math.random() * 50);
    return {
      hour: measurementPoints[i],
      name: labelNames[i],
      x: plotX(hour),
      y: data[hour] < 0.5 ? jitter : height - jitter
    };
  });

  const connectLabel = (label, i, x1, y1) => {
    const [x2, y2] = [plotX(i), plotY(data[i])]
    chart.insert('line', ':first-child')
      .attr('x1', x1)
      .attr('y1', y1)
      .attr('x2', x2)
      .attr('y2', y2)
      .attr('class', 'chart__label-connection');
  }

  labelPositions.forEach(({x, y, name, hour}) => {
    const label = chart.select(`[data-locator="${name}"]`);
    moveLabel(label, x, y);
    connectLabel(label, hour, x, y);
  });
})(window);
