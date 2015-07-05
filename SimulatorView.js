var width = Math.max(940, innerWidth),
	height = Math.max(500, innerHeight);
			
var i = 0;

var svg = d3.select("body").append("svg")
    .attr("width", width)
    .attr("height", height);

svg.append("rect")
    .attr("width", width)
    .attr("height", height)
/*	    .on("ontouchstart" in document ? "touchmove" : "mousemove", particle);

function particle() {
  var m = d3.mouse(this);

  svg.insert("circle", "rect")
      .attr("cx", m[0])
      .attr("cy", m[1])
      .attr("r", 1e-6)
      .style("stroke", d3.hsl((i = (i + 1) % 360), 1, .5))
      .style("stroke-opacity", 1)
    .transition()
      .duration(2000)
      .ease(Math.sqrt)
      .attr("r", 100)
      .style("stroke-opacity", 1e-6)
      .remove();

  d3.event.preventDefault();
}*/

function addUserCircle(username) {
	svg.insert("circle", "rect")
	.attr("cx", width / 2.0 + (Math.random() - 0.5) * width / 1.1)
	.attr("cy", height / 2.0 + (Math.random() - 0.5) * height / 1.1)
	.attr("r", 10)
	.attr("id", "user_" + username);
}

function addSpreadLine(sender, receiver, hexColor) {
	var senderCircle = $("#user_" + sender);
	var receiverCircle = $("#user_" + receiver);

	
	svg.insert("line", "rect")
	.attr("x1", senderCircle.attr("cx"))
	.attr("y1", senderCircle.attr("cy"))
	.attr("x2", senderCircle.attr("cx"))
	.attr("y2", senderCircle.attr("cy"))
	.attr("stroke-width", 2)
	.attr("stroke", hexColor)
  .transition()
  .duration(2000)
  .attr("x2", receiverCircle.attr("cx"))
	.attr("y2", receiverCircle.attr("cy"))
  .transition()
  .duration(10000)
  .attr("stroke-width", 0.5)
  .style("stroke-opacity", 0.5);
}