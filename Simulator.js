var main = function() {

	$("#add-user-submit").click(function() {

		var username = $("#add-user").val();
		$("#add-user").val("");
		var user = new User(username);

		var html = "<li class=\"list-group-item\">" + username + "</li>";
		$("#user-list").append(html);

		// Add user to start a ripple dropdown list. 
		var html = "<li><input value=\"" + username + "\" class=\"user-radio-start\" type=\"radio\" name=\"radio-group\"/>" +
		username + "</li>";
		$("#user-start-ripple-dropdown").append(html);

		// Select user in ripple dropdown list to start
		$(".user-radio-start").click(function() {
			$("#user-start-ripple-dropdown-label").text($(this).val());
		});




		// Add user to spread a ripple dropdown list. 
		var html = "<li><input value=\"" + username + "\" class=\"user-radio-spread\" type=\"radio\" name=\"radio-group\"/>" +
		username + "</li>";
		$("#user-spread-ripple-dropdown").append(html);

		// Select user in ripple dropdown list to start
		$(".user-radio-spread").click(function() {
			$("#user-spread-ripple-dropdown-label").text($(this).val());

			var user = null;

			for (var i = 0; i < users.length; i++) {
				if (users[i].name == $(this).val())
				{ 
					user = users[i];
					break;
				}
			}
			if (user == null)
			{
				return;
			}
			$('#ripple-spread-ripple-dropdown').empty();
			for (var i = 0; i < user.pendingRipples.length; i++)
			{
				var ripple = user.pendingRipples[i];
				// Add user to spread a ripple dropdown list. 
				var html = "<li><input value=\"" + ripple.text + "\" class=\"ripple-radio-spread\" type=\"radio\" name=\"radio-group\"/>" +
				ripple.text + "</li>";
				$("#ripple-spread-ripple-dropdown").append(html);

				$(".ripple-radio-spread").click(function() {
					$("#ripple-spread-ripple-dropdown-label").text($(this).val());
				})
			}



		});

		addUserCircle(username);	
	});

	$("#start-ripple-submit").click(function() {
		var username = $("#user-start-ripple-dropdown-label").text();
		var rippleText = $("#start-ripple-text").val();


		for (var i = 0; i < users.length; i++) {
			if (users[i].name == username) {
				var ripple = users[i].startRipple(rippleText);

				var html = "<li class=\"list-group-item\">" + rippleText + "</li>";
				$("#ripple-list").append(html);
				
				for (var j = 0; j < ripple.receivers.length; j++)
				{
					if (ripple.receivers[j] != users[i])
						addSpreadLine(username, ripple.receivers[j].name);
				}
				

				break;
			}
		}
	});

	$(".ripple-action").click(function() {
		var username = $("#user-spread-ripple-dropdown-label").text();
		var rippleText = $("#ripple-spread-ripple-dropdown-label").text();

		for (var i = 0; i < users.length; i++) {
			if (users[i].name == username) {
				for (var j = 0; j < users[i].pendingRipples.length; j++)
				{
					if (users[i].pendingRipples[j].text == rippleText)
					{
						if (this.id == "spread-ripple-submit") {
							var spreadUsers = users[i].spreadRipple(users[i].pendingRipples[j]);
							for (var k = 0; k < spreadUsers.length; k++) {
								addSpreadLine(username, spreadUsers[k].name);
							}
							
						}
						else if (this.id == "dismiss-ripple-submit") {
							users[i].dismissRipple(users[i].pendingRipples[j]);
						}
						else
							alert ("BOO");

						break;
					}
				}
				break;
			}
		}
	});
};

$(document).ready(main);
