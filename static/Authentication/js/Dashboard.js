// --- Bar Chart: Atención promedio por minutos de la clase ---
const barData = [
    { minuto: 10, atencion: 82 },
    { minuto: 20, atencion: 68 },
    { minuto: 30, atencion: 45 },
    { minuto: 40, atencion: 73 },
    { minuto: 50, atencion: 80 },
    { minuto: 60, atencion: 70 },
    { minuto: 70, atencion: 60 },
    { minuto: 80, atencion: 90 },
    { minuto: 90, atencion: 75 },
    { minuto: 100, atencion: 82 }
];

const barSvg = d3.select("#attentionByClass"),
    barWidth = barSvg.node().getBoundingClientRect().width,
    barHeight = +barSvg.attr("height"),
    margin = { top: 30, right: 30, bottom: 40, left: 50 },
    width = barWidth - margin.left - margin.right,
    height = barHeight - margin.top - margin.bottom;

const barG = barSvg.append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

const x = d3.scaleBand()
    .domain(barData.map(d => d.minuto))
    .range([0, width])
    .padding(0.2);

const y = d3.scaleLinear()
    .domain([0, 100])
    .range([height, 0]);

barG.append("g")
    .attr("transform", `translate(0,${height})`)
    .call(d3.axisBottom(x));

barG.append("g")
    .call(d3.axisLeft(y));

barG.selectAll(".bar")
    .data(barData)
    .enter()
    .append("rect")
    .attr("class", "bar")
    .attr("x", d => x(d.minuto))
    .attr("y", d => y(d.atencion))
    .attr("width", x.bandwidth())
    .attr("height", d => height - y(d.atencion))
    .attr("fill", "#10b981");

// --- Line Chart: Tendencia de atención diaria ---
const lineData = barData; // Puedes cambiar por otros datos si lo deseas

const lineSvg = d3.select("#attentionTrend"),
    lineWidth = lineSvg.node().getBoundingClientRect().width,
    lineHeight = +lineSvg.attr("height"),
    margin2 = { top: 30, right: 30, bottom: 40, left: 50 },
    width2 = lineWidth - margin2.left - margin2.right,
    height2 = lineHeight - margin2.top - margin2.bottom;

const lineG = lineSvg.append("g")
    .attr("transform", `translate(${margin2.left},${margin2.top})`);

const x2 = d3.scalePoint()
    .domain(lineData.map(d => d.minuto))
    .range([0, width2]);

const y2 = d3.scaleLinear()
    .domain([0, 100])
    .range([height2, 0]);

lineG.append("g")
    .attr("transform", `translate(0,${height2})`)
    .call(d3.axisBottom(x2));

lineG.append("g")
    .call(d3.axisLeft(y2));

const line = d3.line()
    .x(d => x2(d.minuto))
    .y(d => y2(d.atencion))
    .curve(d3.curveMonotoneX);

lineG.append("path")
    .datum(lineData)
    .attr("fill", "none")
    .attr("stroke", "#3b82f6")
    .attr("stroke-width", 3)
    .attr("d", line);

lineG.selectAll("circle")
    .data(lineData)
    .enter()
    .append("circle")
    .attr("cx", d => x2(d.minuto))
    .attr("cy", d => y2(d.atencion))
    .attr("r", 5)
    .attr("fill", "#3b82f6");

// --- Fetch and Update Data ---
async function fetchAtencionData() {
    const response = await fetch('/api/ia/atencion/');
    return await response.json();
}

function renderBarChart(data) {
    d3.select("#attentionByClass").selectAll("*").remove();

    const svg = d3.select("#attentionByClass"),
        width = svg.node().getBoundingClientRect().width,
        height = +svg.attr("height"),
        margin = { top: 30, right: 30, bottom: 40, left: 50 },
        w = width - margin.left - margin.right,
        h = height - margin.top - margin.bottom;

    const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

    const x = d3.scaleBand()
        .domain(data.map(d => d.minuto))
        .range([0, w])
        .padding(0.2);

    const y = d3.scaleLinear()
        .domain([0, 100])
        .range([h, 0]);

    g.append("g")
        .attr("transform", `translate(0,${h})`)
        .call(d3.axisBottom(x));

    g.append("g")
        .call(d3.axisLeft(y));

    g.selectAll(".bar")
        .data(data)
        .enter()
        .append("rect")
        .attr("class", "bar")
        .attr("x", d => x(d.minuto))
        .attr("y", d => y(d.atencion))
        .attr("width", x.bandwidth())
        .attr("height", d => h - y(d.atencion))
        .attr("fill", "#10b981");
}

function renderLineChart(data) {
    d3.select("#attentionTrend").selectAll("*").remove();

    const svg = d3.select("#attentionTrend"),
        width = svg.node().getBoundingClientRect().width,
        height = +svg.attr("height"),
        margin = { top: 30, right: 30, bottom: 40, left: 50 },
        w = width - margin.left - margin.right,
        h = height - margin.top - margin.bottom;

    const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

    const x = d3.scalePoint()
        .domain(data.map(d => d.minuto))
        .range([0, w]);

    const y = d3.scaleLinear()
        .domain([0, 100])
        .range([h, 0]);

    g.append("g")
        .attr("transform", `translate(0,${h})`)
        .call(d3.axisBottom(x));

    g.append("g")
        .call(d3.axisLeft(y));

    const line = d3.line()
        .x(d => x(d.minuto))
        .y(d => y(d.atencion))
        .curve(d3.curveMonotoneX);

    g.append("path")
        .datum(data)
        .attr("fill", "none")
        .attr("stroke", "#3b82f6")
        .attr("stroke-width", 3)
        .attr("d", line);

    g.selectAll("circle")
        .data(data)
        .enter()
        .append("circle")
        .attr("cx", d => x(d.minuto))
        .attr("cy", d => y(d.atencion))
        .attr("r", 5)
        .attr("fill", "#3b82f6");
}

async function updateCharts() {
    const data = await fetchAtencionData();
    if (data && data.length > 0) {
        renderBarChart(data);
        renderLineChart(data);
    }
}

updateCharts();
setInterval(updateCharts, 10000);