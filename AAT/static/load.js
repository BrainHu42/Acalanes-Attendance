cookie = get_cookie("remind");

if (document.getElementById("remindInput")) {
  cookie == "yes" ? $("#remindInput").prop("checked", true) : $("#remindInput").prop("checked", false);
}

$("#refresh").ready(function() {
  tardyTime = parseInt("{{ tardyTime }}");
  if (isNaN(tardyTime)) {
    tardyTime = null;
  }
  period = parseInt("{{ period }}");
  if (isNaN(period)) {
    period = null;
  }
  page_load();
});
