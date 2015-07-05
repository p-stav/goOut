var users = [];
var ripples = [];

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
		return usersForRippleSpread;
	}
}