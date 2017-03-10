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
      return "Hot Now!";
    } else {
      return "Not Hot";
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

      function splitIntoDays() {
        $scope.days = [];
        $scope.dayTransitions = {};
        var data = $scope.data;
        var old_ds = null;
        for (var i in data) {
          var ts = data[i][0];
          var lit = data[i][1];
          var d = new Date();
          d.setTime(ts * 1000);
          var ds = d.toDateString();
          if (ds != old_ds) {
            $scope.days.push(ds);
          }
          if (!$scope.dayTransitions[ds]) {
            $scope.dayTransitions[ds] = [];
          }
          $scope.dayTransitions[ds].push([d, lit]);
          old_ds = ds;
        }
      }

      splitIntoDays();
    }]
  };
});