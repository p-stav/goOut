var users = [];
var ripples = [];

var currentUser;
var currentRipple;

function userSort(userA, userB) {
	var currentUserCircle = $("#user_" + currentUser.name);
	// distance between current user and A:
	var userACircle = $("#user_" + userA.name);
	var deltaXA = currentUserCircle.attr("cx") - userACircle.attr("cx");
	deltaXA = deltaXA * deltaXA;
	var deltaYA = currentUserCircle.attr("cy") - userACircle.attr("cy");
	deltaYA = deltaYA * deltaYA;
	var distanceA = Math.sqrt(deltaYA + deltaXA);
	
	// distance between current user and B:
	var userBCircle = $("#user_" + userB.name);
	var deltaXB = currentUserCircle.attr("cx") - userBCircle.attr("cx");
	deltaXB = deltaXB * deltaXB;
	var deltaYB = currentUserCircle.attr("cy") - userBCircle.attr("cy");
	deltaYB = deltaYB * deltaYB;
	var distanceB = Math.sqrt(deltaYB + deltaXB);
	
	
	
	if (distanceA < distanceB) {
		return -1;
	}
	else if (distanceA == distanceB) {
		return 0;
	}
	else {
		return 1;
	}
}

function isReceivedCurrentRipple(user) {
	if (currentRipple.receivers.indexOf(user) == -1) {
		return true;
	}
	else {
		return false;
	}
}

// Ripple
var Ripple = function(user, text) {
	this.receivers = [user];
	this.spread = [user];
	this.dismissed = [];
	
	this.text = text;
	
	ripples.push(this);

	this.addReceivers = function(newReceivers) {
		this.receivers = this.receivers.concat(newReceivers);
	};
	this.addSpreaders = function(newSpreaders) {
		this.spread = this.spread.concat(newSpreaders);
	}
	this.addDismissers = function(newDismissers) {
		this.dismissed = this.dismissed.concat(newDismissers);
	}
	
	this.getPendingUsers = function() {
		var pendingUsers = [];
		for (var i = 0; i < this.receivers; i++) {
			var user = this.receivers[i];
			if ((this.spread.indexOf(user) == -1) && (this.dismissed.indexOf(user) == -1)) {
				pendingUsers.push(user);
			}
		}
		return pendingUsers;
	}
};

var userReach = 10;

// User
var User = function(name) {
	this.name = name;
	this.pendingRipples = [];
	this.index = users.length;
	users.push(this);

	this.startRipple = function(text) {
		var ripple = new Ripple(this, text);
		var newReceivers = this.getUsersForRippleSpread(ripple);

		if (newReceivers.length > 0) {
			ripple.addReceivers(newReceivers);
			
			for (var i = 0; i < newReceivers.length; i++) {
				newReceivers[i].pendingRipples.push(ripple);
			}
		}

		return ripple;
	};

	this.spreadRipple = function(ripple) {
		var newReceivers = this.getUsersForRippleSpread(ripple);
		
		if (newReceivers.length > 0) {
			ripple.addReceivers(newReceivers);
			
			for (var i = 0; i < newReceivers.length; i++) {
				newReceivers[i].pendingRipples.push(ripple);
			}
		}
		
		this.pendingRipples.splice(this.pendingRipples.indexOf(ripple), 1);
		ripple.addSpreaders([this]);

		return newReceivers;
	};

	this.dismissRipple = function(ripple) {
		this.pendingRipples.splice(this.pendingRipples.indexOf(ripple), 1);
		ripple.addDismissers([this]);
		return;
	};
	
	this.getUsersForRippleSpread = function(ripple) {
		var usersForRippleSpread = []
		
		if (inSimulatorView == true) {
			// Find the x closest users
			currentUser = this;
			currentRipple = ripple;
			var sortedUserArray = users.slice().filter(isReceivedCurrentRipple);
			sortedUserArray.sort(userSort);
			var numUsersToSpread = Math.min(userReach, sortedUserArray.length);
			for (var i = 0; i < numUsersToSpread; i++) {
				usersForRippleSpread.push(sortedUserArray[i]);
			}
			
		}
		else {
			// find user with next highest id. // TODO: Wrap
			for ( var i = this.index + 1; i < users.length; i++) {
				if (ripple.receivers.indexOf(users[i]) == -1) {
					usersForRippleSpread.push(users[i]);
					
					break;
				}
			}
			for (var i = this.index - 1; i >= 0; i--) {
				if (ripple.receivers.indexOf(users[i]) == -1) {
					usersForRippleSpread.push(users[i]);
					
					break;
				}
			}
		}
		
		return usersForRippleSpread;
	}
	
	
}