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

// render the y axis, involves adding some custom labels.
function renderYAxis(chart, plot) {
  const height = +chart.attr('height');
  
  const axis = d3.axisLeft(plot).ticks(0).tickSizeOuter(0);

  chart.append('svg:g')
    .attr('class', 'generation-chart__axis')
    .attr('transform', 'translate(30, 0)')
    .call(axis);

  const label100 = chart.append('svg:g').attr('class', 'generation-chart__axis-label')

  label100.append('svg:rect')
    .attr('width', 50)
    .attr('height', 28);

  label100.append('svg:text')
    .attr('y', 16)
    .attr('x', 2)
    .text('100 %');

  const label0 = chart.append('svg:g').attr('class', 'generation-chart__axis-label');

  label0.append('svg:rect')
    .attr('y', height-30)
    .attr('width', 50)
    .attr('height', 30);

  label0.append('svg:text')
    .attr('y', height-5)
    .attr('x', 10)
    .text('0 %');
}

function moveLabel(label, x, y) {
  const labelDim = +label.attr('width');
  label.attr('x', x - labelDim/2).attr('y', y - labelDim/2);
}

(global => {
  const data = global.generationData;
  const chart = d3.select('.generation-chart');

  const plotX = d3.scaleLinear().domain([0, data.length]).range([60, chart.attr('width') - 30]);
  const plotY = d3.scaleLinear().domain([0, 1]).range([chart.attr('height'), 0]);

  renderYAxis(chart, plotY);

  const [obs, pred] = partitionData(data);
  const observed = d3.line().x((d, i) => plotX(i)).y(d => plotY(d)).curve(d3.curveLinear)(obs);
  const predicted = d3.line().x((d, i) => plotX(i + 23) + 5).y(d => plotY(d)).curve(d3.curveLinear)(pred);

  chart.append('svg:path').attr('class', 'generation-chart__line generation-chart__line--mask').attr('d', observed);
  chart.append('svg:path').attr('class', 'generation-chart__line generation-chart__line--mask').attr('d', predicted);
  chart.append('svg:path').attr('class', 'generation-chart__line').attr('d', observed);
  chart.append('svg:path').attr('class', 'generation-chart__line generation-chart__line--predicted').attr('d', predicted);

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
      y: data[hour] < 0.5 ? jitter : chart.attr('height') - jitter
    };
  });

  const connectLabel = (label, i, x1, y1) => {
    const [x2, y2] = [plotX(i), plotY(data[i])]
    chart.insert('line', ':first-child')
      .attr('x1', x1)
      .attr('y1', y1)
      .attr('x2', x2)
      .attr('y2', y2)
      .attr('class', 'generation-chart__label-connection');
  }

  labelPositions.forEach(({x, y, name, hour}) => {
    const label = chart.select(`[data-locator="${name}"]`);
    moveLabel(label, x, y);
    connectLabel(label, hour, x, y);
  });
})(window);
