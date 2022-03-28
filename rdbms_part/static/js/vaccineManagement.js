$(document).ready(function () {});

function onUpdateVaccineModalClick(id, name, type) {
  console.log("onUpdateVaccineModalClick");
  // Open vaccine update modal.
  $("#updateVaccineName").val(name);
  $("#updateVaccineType").val(type);
  $("#updateVaccineId").val(id);
}

function onDeleteVaccineModalClick(id) {
  console.log("onDeleteVaccineModalClick");
  // Open vaccine update modal.
  $("#deleteVaccineId").val(id);
}

function createVaccine() {
  var name = $("#createVaccineName").val();
  var type = $("#createVaccineType").val();
  console.log(name);
  console.log(type);

  axios
    .post("/vaccines", {
      name: name,
      type: type,
    })
    .then(function (response) {
      if (response.data === "success") {
        alert(response.data);
        location.reload();
      } else {
        alert("error please try again!" + response.data);
      }
    })
    .catch(function (error) {
      alert("error please try again!");
      console.log(error);
    });
}

function updateVaccine() {
  var id = $("#updateVaccineId").val();
  var name = $("#updateVaccineName").val();
  var type = $("#updateVaccineType").val();

  axios
    .put(`/vaccines/${id}`, {
      id: id,
      name: name,
      type: type,
    })
    .then(function (response) {
      if (response.data === "success") {
        alert(response.data);
        location.reload();
      } else {
        alert("error please try again!" + response.data);
      }
    })
    .catch(function (error) {
      alert("error please try again!");
      console.log(error);
    });
}

function deleteVaccine() {
  var id = $("#deleteVaccineId").val();

  axios
    .delete(`/vaccines/${id}`)
    .then(function (response) {
      if (response.data === "success") {
        alert(response.data);
        location.reload();
      } else {
        alert("error please try again!" + response.data);
      }
    })
    .catch(function (error) {
      alert("error please try again!");
      console.log(error);
    });
}
