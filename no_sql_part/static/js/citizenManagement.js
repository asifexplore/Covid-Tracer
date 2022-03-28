$(document).ready(function () {});

function getCitizenHistory(id, name) {
  console.log("getCitizenHistoryhh");
  console.log(id);
  console.log(name);

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
      console.log(response.data);
      var isHealthActive = true;
      var isVaccinationctive = true;

      for (let i = 0; i < response.data.length; ++i) {
        var data = response.data[i].historys;
        console.log(data);

        // var isActive = "active" == response.data[i][4] ? "active" : "";

        var message = "";
        if (isHealthActive && data.status !== undefined) {
          message = "<b>";
        }
        if (isVaccinationctive && data.dose_type !== undefined) {
          message = "<b>";
        }

        message +=
          data.dose_type === undefined
            ? "Health status changed to " + data.status
            : data.dose_type + " vaccination shot was taken ";

        if (isHealthActive && data.status !== undefined) {
          message += "</b>";
          isHealthActive = false;
        }
        if (isVaccinationctive && data.dose_type !== undefined) {
          message += "</b>";
          isVaccinationctive = false;
        }

        timeline +=
          "<div class='tl-item " +
          // isActive +
          "'><div class='tl-dot'></div><div class='tl-content'><div>" +
          message +
          "</div><div class='text-muted mt-1'>Updated By: " +
          data.updated_by_name +
          // data[i][1] +
          ", on " +
          data.updated_at +
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
      console.log(response.data);
      for (let i = 0; i < response.data.length; ++i) {
        var data = response.data[i].footprints;
        var isActive = i == 0 ? "active" : "";

        var message = "";
        if (isActive) {
          message = "<b>";
        }

        message += "Went to " + data.landmark_name;

        if (isActive) {
          message += "</b>";
        }

        timeline +=
          "<div class='tl-item " +
          isActive +
          "'><div class='tl-dot'></div><div class='tl-content'><div>" +
          message +
          "</div><div class='text-muted mt-1'>" +
          data.updated_at +
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
  console.log("insertFootprints");
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
