angular.module('HotDonuts', [])
.controller('DonutsController', ['$scope','$http', function($scope, $http) {
  function populateLocations(data) {
    $scope.locations = data.data;
  }

  function populateCurrent(data) {
    $scope.currents = data.data;
  }

  function populateLocation(id) {
    return function(data) {
      $scope.locationHistory[id] = data;
    }
  }

  $scope.hotStatus = function(id) {
    if ($scope.currents[id] == 1) {
      return "Hot Now";
    } else {
      return "Not";
    }
  };

  $scope.locationHistory = {};
  $scope.expanded = {};
  $scope.toggleExpanded = function(id) {
    $scope.expanded[id] = !$scope.expanded[id];
    if ($scope.expanded[id]) {
      debugger;
      $http.get("http://live.hotdonuts.info/" + id + ".data").then(populateLocation(id));
    }
  };

  $http.get("http://live.hotdonuts.info/current.data").then(populateCurrent);
  $http.get("http://live.hotdonuts.info/locations.data").then(populateLocations);
}]);
