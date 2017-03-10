var hd = angular.module('HotDonuts', []);

hd.controller('DonutsController', ['$scope','$http', function($scope, $http) {
  function populateLocations(data) {
    $scope.locations = data.data;
  }

  function populateCurrent(data) {
    $scope.currents = data.data;
  }

  function populateLocation(id) {
    return function(data) {
      $scope.locationHistory[id] = data.data;
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
      $http.get("http://live.hotdonuts.info/" + id + ".data").then(populateLocation(id));
    }
  };

  $http.get("http://live.hotdonuts.info/current.data").then(populateCurrent);
  $http.get("http://live.hotdonuts.info/locations.data").then(populateLocations);
  }]);

hd.directive("hothistory", function() {
  return {
    templateUrl: 'hothistory.html',
    replace: true,
    scope: {
      data: "=data"
    },

    controller: ['$scope', function($scope) {
    }]

  };
});
