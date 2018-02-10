import '../scss/main.scss';
import * as d3 from 'd3';

(global => {
  const chart = d3.select('#chart');
  const width = +chart.attr('width');
  const height = +chart.attr('height');

  const x = d3.scaleLinear().domain([0, global.generationData.length]).range([30, width - 30]);
  const y = d3.scaleLinear().domain([0, 1]).range([height, 0]);

  const observed = d3.line().x((d, i) => x(i)).y(d => y(d)).curve(d3.curveLinear);
  const predicted = d3.line().x((d, i) => x(i + 23) + 5).y(d => y(d)).curve(d3.curveLinear);

  const yAxis = d3.axisLeft(y);
  chart.append('svg:g')
    .attr('class', 'axis axis--y')
    .call(yAxis);

  const obs = global.generationData.slice(0, 24);
  const pred = global.generationData.slice(24);
  pred.unshift(obs[obs.length - 1]);

  chart.append('svg:path').attr('class', 'line').attr('d', observed(obs));
  chart.append('svg:path').attr('class', 'line line--predicted').attr('d', predicted(pred));

})(window);

