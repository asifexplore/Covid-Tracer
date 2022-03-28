$(document).ready(function () {
  $("#viewCitizensinClusters").on("hidden.bs.modal", function (e) {
    $("#citizensinClusterData").empty();
  });
});

function cleanDoB(DoB) {
  // Clean dob of citizen.
  let clean = DoB.slice(0, 16);
  return clean;
}

function getCitizensinCluster(cluster_id) {
  // Set loading.
  $("#clusterData").css("display", "none");
  $("#clusterLoading").css("display", "block");

  //   POST to get all citizen in landmark.
  axios
    .post("/get-citizens-in-cluster", {
      cluster_id: cluster_id,
    })
    .then(function (response) {
      $("#clusterData").css("display", "block");
      $("#clusterLoading").css("display", "none");
      if (response.data == null) {
        $("#nodata")
          .attr("class", "alert alert-danger")
          .html(
            "Something went wrong, unable to display citizens in cluster data"
          );
        return;
      }

      for (let i = 0; i < response.data.length; ++i) {
        var nric = response.data[i][1];
        var fullName = response.data[i][2];
        var most_recent_dose = response.data[i][3];
        var most_recent_status = response.data[i][4];
        var address = response.data[i][5];
        var mobile = response.data[i][6];
        var dob = response.data[i][7];
        var cleanedDoB = cleanDoB(dob);
        var gender = response.data[i][8];
        $("#citizensinClusterData").append(
          "" +
            "<tr>" +
            "<td>" +
            nric +
            "</td>" +
            "<td>" +
            fullName +
            "</td>" +
            "<td>" +
            most_recent_dose +
            "</td>" +
            "<th scope='row'>" +
            most_recent_status +
            "</th>" +
            "<td>" +
            address +
            "</td>" +
            "<td>" +
            mobile +
            "</td>" +
            "<td>" +
            cleanedDoB +
            "</td>" +
            "<td>" +
            gender +
            "</td>" +
            "</tr>"
        );
      }
    })
    .catch(function (error) {
      console.log(error);
    });
}

function detectAndUpdateClusters() {
  // POST request to detect and update changes to clusters.
  axios
    .post("/detect-update-clusters", {})
    .then(function (response) {
      alert(response.data);
      location.reload();
    })
    .catch(function (error) {
      alert(response.data);
      console.log(error);
    });
}
