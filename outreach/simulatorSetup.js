function djb2(str){
  var hash = 5381;
  for (var i = str.length - 1; i >= 0; i--) {
    hash = ((hash << 5) + hash) + str.charCodeAt(i); /* hash * 33 + c */
  }
  return hash;
}

function hashRippleToColor(ripple) {
  var hash = djb2(ripple.text);
  var r = (hash & 0xFF0000) >> 16;
  var g = (hash & 0x00FF00) >> 8;
  var b = hash & 0x0000FF;
  return "#" + ("0" + r.toString(16)).substr(-2) + ("0" + g.toString(16)).substr(-2) + ("0" + b.toString(16)).substr(-2);
}

var startInterval;
var spreadInterval;
var startCounter = 0;
var spreadCounter = 0;

function startRipple() {
	if (startCounter == 3) {
		clearInterval(startInterval);
		spreadInterval = setInterval(spreadRipple, 400);
		return;
	}
	// pick random user to start the ripple
	var userIndex = Math.floor(Math.random() * users.length);
	var user = users[userIndex];
	var ripple = user.startRipple("text_" + startCounter.toString());
	for (var j = 0; j < ripple.receivers.length; j++)
	{
		if (ripple.receivers[j] != user)
			 addSpreadLine(user.name, ripple.receivers[j].name, hashRippleToColor(ripple));
	}
	startCounter++;
}


var currentRippleInSimulator;
function isUserPending(user) {
	if ((currentRippleInSimulator.spread.indexOf(user) == -1) && (currentRippleInSimulator.dismissed.indexOf(user) == -1)) {
		return true;
	}
	else {
		return false;
	}
}

function spreadRipple() {
	if (spreadCounter == 50) {

		clearInterval(spreadInterval);
		restartSimulation();
	}

	var rippleIndex = Math.floor(Math.random() * ripples.length);
	var ripple = ripples[rippleIndex];
	
	// attempt to spread
	currentRippleInSimulator = ripple;
	var pendingUsers = ripple.receivers.slice().filter(isUserPending);
	var userIndex = Math.floor(Math.random() * pendingUsers.length);
	var user = pendingUsers[userIndex];
	
	var newReceivers = user.spreadRipple(ripple);
	for (var j = 0; j < newReceivers.length; j++) {
		addSpreadLine(user.name, newReceivers[j].name, hashRippleToColor(ripple));
			
	}
	 
	spreadCounter++;
}


startInterval = setInterval(startRipple, 500);