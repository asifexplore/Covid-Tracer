$(document).ready(function () {});

function getCitizenHistory(id, name) {
  console.log("getCitizenHistory");
  // Set loading.
  $("#historyData").css("display", "none");
  $("#historyLoading").css("display", "block");

  // Place name of citizen in modal.
  $("#historyName").text(name);

  // POST request to get citizen history.
  axios
    .post("/get-citizen-history", {
      citizen_id: id,
    })
    .then(function (response) {
      // Set data.
      $("#historyData").css("display", "block");
      $("#historyLoading").css("display", "none");

      var timeline = "";

      // If not data, set data not available.
      if (response.data.length == 0) {
        $("#timeline").html("<p>No data available.</p>");
        return;
      }

      // Loop and set data in HTML.
      for (let i = 0; i < response.data.length; ++i) {
        var isActive = "active" == response.data[i][4] ? "active" : "";

        var message = "";
        if (isActive) {
          message = "<b>";
        }

        message +=
          "health" == response.data[i][3]
            ? "Health status changed to " + response.data[i][0]
            : response.data[i][0] + " vaccination shot was taken ";

        if (isActive) {
          message += "</b>";
        }

        timeline +=
          "<div class='tl-item " +
          isActive +
          "'><div class='tl-dot'></div><div class='tl-content'><div>" +
          message +
          "</div><div class='text-muted mt-1'>Updated By: " +
          response.data[i][1] +
          ", on " +
          response.data[i][2] +
          "</div></div></div>";
      }

      $("#timeline").html(timeline);
    })
    .catch(function (error) {
      console.log(error);
      alert("error boi");
    });
}

function getCitizenFootprints(id, name) {
  // Set loading.
  $("#footprintData").css("display", "none");
  $("#footprintLoading").css("display", "block");

  // Place name of citizen in modal.
  $("#footprintName").text(name);

  // POST request to get citizen footprints.
  axios
    .post("/get-citizen-footprints", {
      citizen_id: id,
    })
    .then(function (response) {
      // Set data.
      $("#footprintData").css("display", "block");
      $("#footprintLoading").css("display", "none");

      var timeline = "";

      // If not data, set data not available.
      if (response.data.length == 0) {
        $("#footprintTimeline").html("<p>No data available.</p>");
        return;
      }

      // Loop and set data in HTML.
      for (let i = 0; i < response.data.length; ++i) {
        var isActive = i == 0 ? "active" : "";

        var message = "";
        if (isActive) {
          message = "<b>";
        }

        message +=
          "When to " + response.data[i][0] + ", " + response.data[i][1];

        if (isActive) {
          message += "</b>";
        }

        timeline +=
          "<div class='tl-item " +
          isActive +
          "'><div class='tl-dot'></div><div class='tl-content'><div>" +
          message +
          "</div><div class='text-muted mt-1'>" +
          response.data[i][2] +
          "</div></div></div>";
      }

      $("#footprintTimeline").html(timeline);
    })
    .catch(function (error) {
      console.log(error);
      alert("error boi");
    });
}

function onUpdateCitizenHealthHistoryModalClick(id, name, lastHistory) {
  // Open health history update modal.
  $("#updateHealthSelect select").val(lastHistory);
  $("#updateHealthName").text(name);
  $("#updateHealthId").val(id);
}

function updateCitizenHealthHistory(adminId) {
  var healthSelect = $("#updateHealthSelect select").val().toLowerCase();
  var citizenId = $("#updateHealthId").val();

  // POST to update health history of citizen.
  axios
    .post("/update-health-history", {
      citizen_id: citizenId,
      admin_id: adminId,
      new_status: healthSelect,
    })
    .then(function (response) {
      alert(response.data);
      location.reload();
    })
    .catch(function (error) {
      alert(response.data);
      console.log(error);
    });
}

function onUpdateCitizenVaccinationHistoryModalClick(id, name, lastHistory) {
  // Open vaccination history update modal.
  $("#updateVaccinationSelect select").val(lastHistory);
  $("#updateVaccinationName").text(name);
  $("#updateVaccinationId").val(id);
}

function updateCitizenVaccinationHistory(adminId) {
  var vaccinationSelect = $("#updateVaccinationSelect select")
    .val()
    .toLowerCase();

  // Get all vaccination data.
  vaccinationSelect = vaccinationSelect.split(" ").join("_");
  var citizenId = $("#updateVaccinationId").val();
  var vaccineSelect = $("#updateVaccineSelect select").val();

  // POST to update health history of citizen.
  axios
    .post("/update-vaccination-history", {
      citizen_id: citizenId,
      admin_id: adminId,
      new_dose_type: vaccinationSelect,
      vaccine_id: vaccineSelect,
    })
    .then(function (response) {
      alert(response.data);
      location.reload();
    })
    .catch(function (error) {
      alert(response.data);
      console.log(error);
    });
}

function searchCitizen() {
  // Get search value and GET method.
  location.href = "/manage-citizen?search=" + $("#searchCitizenInput").val();
}

function insertFootprints() {
  var range = $("#insertFootprintsRangeSelect select").val();
  console.log(range);

  axios
    .post("/insert-citizen-footprints", {
      range: range,
    })
    .then(function (response) {
      alert(response.data);
      // location.reload();
    })
    .catch(function (error) {
      alert(response.data);
      // console.log(error);
    });
}
