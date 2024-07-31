$(document).ready(function () {
  $("#keyword").on("input", function () {
    var keyword = $(this).val();
    if (keyword.length > 2) {
      $.ajax({
        url: "/courses",
        method: "GET",
        data: { keyword: keyword },
        success: function (response) {
          $("#course-title").empty();
          $("#course-title").append(
            '<option value="">Select a course</option>'
          );
          response.courses.forEach(function (course) {
            $("#course-title").append(
              '<option value="' + course + '">' + course + "</option>"
            );
          });
        },
      });
    } else {
      $("#course-title").empty();
      $("#course-title").append('<option value="">Select a course</option>');
    }
  });

  $("#recommendation-form").on("submit", function (e) {
    e.preventDefault();
    var course_title = $("#course-title").val();
    $.ajax({
      url: "/recommend",
      method: "GET",
      data: { course_title: course_title },
      success: function (response) {
        $("#recommendations").empty();
        if (response.error) {
          $("#recommendations").append(
            '<li class="list-group-item">' + response.error + "</li>"
          );
        } else {
          $("#recommendations-section").show();
          response.recommendations.forEach(function (course) {
            $("#recommendations").append(
              '<li class="list-group-item"><h5>' +
                course["Course Name"] +
                "</h5><p><strong>Course Description:</strong> " +
                (course["Course Description"] || "") +
                '</p><p><a href="' +
                course["Course URL"] +
                '" target="_blank">Course Link</a></p><p>University: ' +
                course["University"] +
                "</p><p>Rating: " +
                course["Course Rating"] +
                "</p></li>"
            );
          });
        }
      },
    });
  });

  $("#clear-button").on("click", function () {
    $("#recommendation-form")[0].reset();
    $("#course-title")
      .empty()
      .append('<option value="">Select a course</option>');
    $("#recommendations").empty();
    $("#recommendations-section").hide();
  });
});
