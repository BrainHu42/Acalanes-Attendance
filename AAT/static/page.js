$(document).ready(function () {
	$("#date").html(showDate());

	if ($("#absent").children().length == 1) {
		$("#absent").append("<p class='center' style='font-size: 14px;'><em>No absences!</em></p>");
	}
	if ($("#tardy").children().length == 1) {
		$("#tardy").append("<p class='center' style='font-size: 14px;'><em>No tardies yet!</em></p>");
	}
	if ($("#strangerArea").children().length == 0) {
		$("#strangerArea").append("<p class='center'><em>No strangers yet!</em></p>");
	}

	$("#refresh").click(function () {
		location.reload();
	});
});

function checkPass(input) {
	input.value != document.getElementById("password").value ? input.setCustomValidity("Passwords must match") : input.setCustomValidity('');
}

function pageLoad() {
	if (date.getDay() > 0 && date.getDay() < 6) {
		refreshAt(8, 30, Math.floor(Math.random() * 60));
		refreshAt(9, 0, Math.floor(Math.random() * 60));
		refreshAt(10, 5, Math.floor(Math.random() * 60));
		refreshAt(12, 40, Math.floor(Math.random() * 60));
		refreshAt(14, 5, Math.floor(Math.random() * 60));
		if (period == 8) {
			setRefresh(9, 0);
		}
		if (period == 1 || period == 4) {
			setRefresh(8, 30);
		}
		if (period == 2 || period == 5) {
			setRefresh(10, 5);
		}
		if (period == 3 || period == 6) {
			setRefresh(12, 40);
		}
		if (period == 7 || period == 0) {
			setRefresh(14, 5);
		}
	}
}

function removeAbsence(element, student, cohort) {
	if (!confirm("Would you like to temporarily remove "+student+" from the absence list today?")) {
		element.href = "javascript:void(0)";
	}
	else {
		if (cohort.indexOf('C') > -1) {
			changeToInPerson(element, student);
		}
		else {
			changeToRemote(element,student);
		}
	}
}

function changeToRemote(element, student) {
	if (!confirm("Would you like to permanently change "+student+" to completely remote?")) {
		element.href = Flask.url_for('account.removeAbsence', { "name": student, "boolean": "temp" })
	}
	else {
		element.href = Flask.url_for('account.removeAbsence', { "name": student, "boolean": "perm" })
	}
}

function changeToInPerson(element, student) {
	if (!confirm("Would you like to permanently change "+student+" to in-person?")) {
		element.href = Flask.url_for('account.removeAbsence', { "name": student, "boolean": "temp" })
	}
	else {
		element.href = Flask.url_for('account.removeAbsence', { "name": student, "boolean": "perm" })
	}
}