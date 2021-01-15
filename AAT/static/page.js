$(document).ready(function() {
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

  $("#refresh").click(function() {
    location.reload();
  });
});

function checkPass(input) {
  input.value != document.getElementById("password").value ? input.setCustomValidity("Passwords must match") : input.setCustomValidity('');
}

function page_load() {
  if (date.getDay() > 0 && date.getDay() < 6) {
    refresh_at(9, 0, Math.floor(Math.random() * 60));
    refresh_at(10, 30, Math.floor(Math.random() * 60));
    refresh_at(11, 30, Math.floor(Math.random() * 60));
    refresh_at(12, 30, Math.floor(Math.random() * 60));
    refresh_at(13, 30, Math.floor(Math.random() * 60));
    refresh_at(14, 0, Math.floor(Math.random() * 60));
    if (period == 1 || period == 8) {
      top_of_hour(9);
    }
    if (period == 2) {
      bottom_of_hour(10);
    }
    if (period == 3) {
      bottom_of_hour(12);
    }
    if (period == 4) {
      top_of_hour(10);
    }
    if (period == 5) {
      bottom_of_hour(11);
    }
    if (period == 6) {
      bottom_of_hour(13);
    }
    if (period == 7) {
      top_of_hour(14);
    }
  }
}
