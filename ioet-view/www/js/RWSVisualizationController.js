available_nodes = [];
var wires = [];
var selected = null;

var manifestURL = "https://github.com/UCB-IoET/svc/blob/master/manifest.json";


function setupDropShadows(svg) {
	// filter chain comes from:
	// https://github.com/wbzyl/d3-notes/blob/master/hello-drop-shadow.html
	// cpbotha added explanatory comments
	// read more about SVG filter effects here: http://www.w3.org/TR/SVG/filters.html
	 
	// filters go in defs element
	var defs = svg.append("defs");
	 
	// create filter with id #drop-shadow
	// height=130% so that the shadow is not clipped
	var filter = defs.append("filter")
	    .attr("id", "drop-shadow")
	    .attr("height", "150%")
 	    .attr("width", "150%");

	// SourceAlpha refers to opacity of graphic that this filter will be applied to
	// convolve that with a Gaussian with standard deviation 3 and store result
	// in blur
	filter.append("feGaussianBlur")
	    .attr("in", "SourceAlpha")
	    .attr("stdDeviation", 3)
	    .attr("result", "blur");
	 
	// translate output of Gaussian blur to the right and downwards with 2px
	// store result in offsetBlur
	filter.append("feOffset")
	    .attr("in", "blur")
	    .attr("dx", 0)
	    .attr("dy", 0)
	    .attr("result", "offsetBlur");
	 
	// overlay original SourceGraphic over translated blurred opacity by using
	// feMerge filter. Order of specifying inputs is important!
	var feMerge = filter.append("feMerge");
	 
	feMerge.append("feMergeNode")
	    .attr("in", "offsetBlur")
	feMerge.append("feMergeNode")
	    .attr("in", "SourceGraphic");
}

function startVisualization() {

	var svg = d3.select('body').append('svg')
    .attr('width', 320)
    .attr('height', 400);

    setupDropShadows(svg);

    refreshVisualization();
}

function refreshVisualization() {
	visNodes = [];

	available_nodes.forEach(function (node) {
		visNodes.push(new VisualizationNode(node));
	});

	visualize();
}

function forceVis() {
	var svg = d3.select('svg');
	//svg.selectAll("*").remove();

	force = d3.layout.force()
	    .size([400, 400])
	    .nodes(visNodes)
	    .links(wires);

	force.linkDistance(120);

	force.gravity(0);

	var link = svg.selectAll('line').data(wires);

	var node = svg.selectAll('.node').data(visNodes);

    force.on('tick', function() {

	    // When this function executes, the force layout
	    // calculations have concluded. The layout will
	    // have set various properties in our nodes and
	    // links objects that we can use to position them
	    // within the SVG container.

	    // First let's reposition the nodes. As the force
	    // layout runs it updates the `x` and `y` properties
	    // that define where the node should be centered.
	    // To move the node, we set the appropriate SVG
	    // attributes to their new values. We also have to
	    // give the node a non-zero radius so that it's visible
	    // in the container.
	    node.attr('transform', function(d) { return 'translate( ' + d.x + ',' + d.y +')'; })
		
	    // We also need to update positions of the links.
	    // For those elements, the force layout sets the
	    // `source` and `target` properties, specifying
	    // `x` and `y` values in each case.

	    link.attr('x1', function(d) { return d.source.x; })
	        .attr('y1', function(d) { return d.source.y; })
	        .attr('x2', function(d) { return d.target.x; })
	        .attr('y2', function(d) { return d.target.y; });

	});

	// Okay, everything is set up now so it's time to turn
	// things over to the force layout. Here we go.

	force.start();
}

function visualize() {
	var svgContainer = d3.select('svg');

	//returns all the nodes
	var nodeGs = svgContainer.selectAll("g")
		.data(visNodes);

	//only the new nodes that just got added
	var nodeEnter = nodeGs.enter().append("g");
	nodeGs
		.attr('transform', function(d) { return 'translate( ' + d.x + ',' + d.y +')'; })
		.attr('class', 'node')
		.on('mousedown', function() {
			if(selected && selected.node.id != this.__data__.node.id) {
				wires.push(new RWSWire(selected, this.__data__));
				selected.selected = false;
				selected = null;
				visualize()
			} else if(selected) {
				selected.selected = false;
				selected = null;
			} else {
				this.__data__.selected = true;
				selected = this.__data__;
			}
			visualize()
		});
	//Add circles
	nodeEnter.append("circle")

	//all the circle elements
	var circles = nodeGs.selectAll("circle");
	var circleAttributes = circles
		.attr("cx", function (d) { return 0; })
		.attr("cy", function (d) { return 0; })
		.attr("r", function (d) { return d.r; })
		.attr("fill", "purple")
		.style("filter", function(d) { 
			if(selected && selected.node.id == d.node.id) {
				return "url(#drop-shadow)";
			}
			return "";
		});

	
	nodeEnter.append("text");

	//all the text elements
	var texts = nodeGs.selectAll("text");
	//Add Labels
	var textLabels = texts
	    .attr("dy", ".35em")
		.text(function (d) { return d.node.name; })
		.style("font-size", function(d) {
         return Math.min(2 * d.r, (2 * d.r - 8) / this.getComputedTextLength() * 16) + "px"; 
       	})
		.attr("y", function(d) { return 0; })
		.attr("x", function(d) { return - this.getComputedTextLength()/2; })


	var links = svgContainer.selectAll("line")
		.data(wires);

	var linksEnter = links.enter().append("line");
	links
		.attr("x1", function(d) { return d.source.x})
		.attr("y1", function(d) { return d.source.y})
		.attr("x2", function(d) { return d.target.x})
		.attr("y2", function(d) { return d.target.y})
		.attr("stroke-width", 2)
		.attr("stroke", "black");

}

function show_add_popup() {
	document.getElementById('addNodeMask').style.display = "block";
}

function add_node() {
	var name = d3.select('#addNodeName').property('value');
	var type = d3.select('#addNodeType').property('value');
	var node = new RWSSensor(name);
	available_nodes.push(node);
	visNodes.push(new VisualizationNode(node));
	d3.select('#addNodeName').property('value','');
	d3.select('#addNodeType').property('value','');
	document.getElementById('addNodeMask').style.display = "none";
	visualize();
}

function find_nearby_nodes() {
	// document.getElementById('findNodeMask').style.display = "block";
	//here we look for nearby nodes using svcd
	//hardcoded for now
	console.log(available_nodes);
	smap = new RWSSMAPInterface('http://proj.storm.pm:8081/data/buildinggeneral', available_nodes);
	smap.find_nodes();
}

window.addEventListener("DOMContentLoaded", function() {
    startVisualization()
}, false);