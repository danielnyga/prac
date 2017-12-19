var chartEl = document.getElementById("chart", true, true),
    w = chartEl.offsetWidth,
    h = chartEl.offsetHeight,

    force = d3.layout.force(),

    svg = d3.select("#chart")
    .append("svg:svg")
    .attr("width", '100%')
    .attr("height", '100%')
    .attr("align","center")
    .append( "svg:g" )
    .attr('class', 'graph'),

    _markertypes = ["red", "green", "black", "blue"],
    svgContainer = svg.select('g.graph'),
    _defs = svgContainer.append("defs");

d3.json("_static/js/mrfgraph.json", function(json) {
    console.log('links:', json.links, 'nodes', json.nodes);
    console.log('svgcontainer', svgContainer);
    _markers = _defs.selectAll("marker").data(_markertypes);

    _markers
        .enter()
        .append("marker")
        .attr("id", function(d) { return d; })
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 10)
        .attr("refY", -.8)
        .attr("markerWidth", 7.5)
        .attr("markerHeight", 7.5)
        .attr("orient", "auto")
        .append("path")
        .attr("d", "M0,-5L10,0L0,5 Z");

    console.log('markers', _markers);

    var links = svgContainer.selectAll("path.link").data(json.links, function(d) {return d.source.id + "-" + d.target.id;});

    console.log('links', links);
    links
        .enter()
        .append("path")
        .attr("id", function(d) { console.log('appending link with id', d.source.id); return d.source.id + "-" + d.target.id; })
        .attr("class", function(d) { return "link " + d.arcStyle; })
        .attr("marker-end", function(d) {
            var split = d.arcStyle.split(' ');
            var as = split[split.length-1];
            return "url(#" + as + ")"; });

    var linklabels = svgContainer.selectAll(".linklabel").data(json.links, function(d) {return d.source.id + "-" + d.target.id;});

    linklabels
        .enter()
        .append('text')
        .style("pointer-events", "none")
        .attr('class', 'linklabel')
        .text(function(d){ return d.value.join(' / '); });

    var circles = svgContainer.selectAll("g.node").data(json.nodes, function(d) { return d.id; } );

    // create nodes group
    var circleEnter = circles
        .enter()
        .append("g")
        .attr("class", "node")
        .call(force.drag);

    // create nodes
    circleEnter.append("svg:circle")
        .on("mouseover", function(d) {
            tooltip
                .transition(200)
                .style("display", "inline");
        })
        .on('mousemove', function(d) {
            var absoluteMousePos = d3.mouse(this);
            var absoluteMousePos = d3.mouse(that._svgContainer.node());
            var newX = (absoluteMousePos[0] + 20);
            var newY = (absoluteMousePos[1] - 20);

            tooltip
                .text(d.text)
                .attr('x', (newX) + "px")
                .attr('y', (newY) + "px");

        })
        .on("mouseout", function(d) {
            tooltip
                .transition(200)
                .style("display", "none");
        })
        .attr('class', function(d) {
            if (typeof(d.type) == 'undefined') {
                return 'graphcircle';
            } else {
                return d.type;
            }
        })
        .attr("r", function(d) {
            d.radius = 10;
            return d.radius;
        })
        .attr("id", function(d) { return d.id; } );

    // create node labels
    circleEnter.append("svg:text")
        .attr("class","textClass")
        .attr("dx", function (d) { return 5; }) // move inside rect
        .attr("dy", function (d) { return 15; }) // move inside rect
        .text( function(d) { return d.id; } );

    var tick = function () {
        links.attr("d", linkArc);

        linklabels
            .attr('d', linkArc)
            .attr('transform', rotateLabel)
            .attr('x', transformLabelX)
            .attr('y', transformLabelY);

        circles.attr("transform", transform);
    };

    var rotateLabel = function (d) {
        var bbox = this.getBBox();
        var rx = bbox.x+bbox.width/2;
        var ry = bbox.y+bbox.height/2;
        var dX = d.target.x - d.source.x;
        var dY = d.target.y - d.source.y;
        var rad = Math.atan2(dX, dY);
        var deg = -90-rad * (180 / Math.PI);
        return 'rotate(' + deg +' '+rx+' '+ry+')';
    };


    var linkArc = function (d) {

        var dx = d.target.x - d.source.x,
            dy = d.target.y - d.source.y,
            dr = Math.sqrt(dx * dx + dy * dy);

            // offset to let arc start and end at the edge of the circle
            var offSetX = (dx * d.target.radius) / dr;
            var offSetY = (dy * d.target.radius) / dr;
        return "M" +
            (d.source.x + offSetX) + "," +
            (d.source.y + offSetY) + "A" +
            dr + "," + dr + " 0 0,0 " +
            (d.target.x - offSetX) + "," +
            (d.target.y - offSetY);
    };

    // move arc label to arc
    var calcLabelPos = function (d, bbox) {
        var scale = 0.4; // distance from arc
        var origPos = { x: (d.source.x + d.target.x ) /2 - bbox.width/2, y: (d.source.y + d.target.y) /2 }; // exact middle between source and target
        var dir = { x: d.target.x - d.source.x, y: d.target.y - d.source.y }; // direction source -> target
        var rot = { x: dir.y, y: -dir.x }; // rotate direction -90 degrees
        var ltemp = Math.sqrt(rot.x * rot.x + rot.y * rot.y) / 100; // normalize length
        var length = ltemp !== 0 ? ltemp : 0.1; // if length is 0, set to small value to prevent NaN
        var rotNorm = { x: rot.x / length, y: rot.y / length }; // normalize rotation direction
        return { x: origPos.x - scale * rotNorm.x, y: origPos.y - scale * rotNorm.y};// return moved position
    };

    var transform = function (d) {
        return "translate(" + d.x + "," + d.y + ")";
    };

    var transformLabel = function (d) {
        return "translate(" + d.source.x + "," + d.source.y + ")";
    };

    var transformLabelX = function (d) {
        var bbox = this.getBBox();
        return calcLabelPos(d, bbox).x;
    };

    var transformLabelY = function (d) {
        var bbox = this.getBBox();
        return calcLabelPos(d, bbox).y;
    };

    force
        .size([w, h])
        .linkDistance( 150 )
        .charge( -700 )
        .on("tick", tick)
        .gravity( .1 )
        .start();

    // tooltip
    var tooltip = svg.selectAll(".tooltip").data([1]);

    // create tooltip
    tooltip
        .enter()
        .append('text')
        .attr('class', 'tooltip')
        .style('display', 'none')
        .style('fill', '#89a35c')
        .style('z-index', 1000000)
        .style('font-family', 'sans-serif')
        .style('font-size', '13px')
        .style('font-weight', 'bold');
});
