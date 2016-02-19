(function () {

    angular.module('myapp', ['ngMaterial'])
    .controller('AppCtrl', function($scope, $http) {
        $http({
                  method : "GET",
                  url : "/jobs"
              }
            ).then(function(response) {
                $scope.data = response.data;
                var tmp = $scope.data.length;
                $scope.cnt = tmp === 0?"keine aktive Stelle":tmp === 1 ? "Eine aktive Stelle" : "Insgesamt "+tmp + " Stellen";
            }
        );
    });
})();