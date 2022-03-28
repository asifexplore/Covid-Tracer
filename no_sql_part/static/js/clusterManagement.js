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

function getCitizensinCluster(landmark_id) {
  // Set loading.
  $("#clusterData").css("display", "none");
  $("#clusterLoading").css("display", "block");

  //   POST to get all citizen in landmark.
  axios
    .post("/get-citizens-in-cluster", {
      landmark_id: landmark_id,
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
      var count = 0;
      for (let i = 0; i < response.data.length; ++i) {
        count+=1;
        console.log(response.data[i]);
        var nric = response.data[i][0];
        var fullName = response.data[i][1];
        var most_recent_status = response.data[i][2];
        var address = response.data[i][3];
        var mobile = response.data[i][4];
        var DoB = response.data[i][5];
        var gender = response.data[i][6];
        $("#citizensinClusterData").append(
          "" +
            "<tr>" +
            "<td>" +
            nric +
            "</td>" +
            "<td>" +
            fullName +
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
            DoB +
            "</td>" +
            "<td>" +
            gender +
            "</td>" +
            "</tr>"
        );
      }
      console.log(count);
      $("#citizensinClusterModalTitle").empty().append('No of Citizens in Cluster: ' + count)
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
