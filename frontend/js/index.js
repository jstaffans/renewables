import '../scss/main.scss';
import * as d3 from 'd3';

(global => {
  const chart = d3.select('#chart');
  const width = +chart.attr('width');
  const height = +chart.attr('height');

  debugger;
  const x = d3.scaleLinear().domain([0, global.generationData.length]).range([40, width - 40]);
  const y = d3.scaleLinear().domain([0, 1]).range([height, 0]);
  const line = d3.line().x((d, i) => {
    console.log(`Plotting ${i} to be at ${x(i)}`);
    return x(i);
  }).y(d => y(d));

  // const xAxis = d3.axisBottom(x);
  // chart.append('svg:g')
  //   .attr('class', 'axis--x')
  //   .attr('transform', `translate(0, ${height})`)
  //   .call(xAxis);

  const yAxis = d3.axisLeft(y);
  chart.append('svg:g')
    .attr('class', 'axis--y')
    .call(yAxis);

  chart.append('svg:path').attr('d', line(global.generationData));

})(window);

