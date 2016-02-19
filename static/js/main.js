(function () {

    var app = angular.module('myapp', ['ngMaterial'])
    .controller('AppCtrl', function($scope, $http, $mdToast) {
        var refresh = function(){
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
        }

        refresh();

        $scope.queryURL = "";

        $scope.submitNewURLQuery = function(e){
            if(e.keyCode == 13){
                $http({
                          method : "POST",
                          url : "/add",
                          data : "url=" + $scope.queryURL,
                          headers : {
                                "Content-Type" : "application/x-www-form-urlencoded"
                          }
                      }
                    ).then(function(response) {
                        refresh();
                        if(response.data.trim() == "OK"){
                            $mdToast.show(
                              $mdToast.simple()
                                .textContent('OK')
                                .position("bottom right")
                                .hideDelay(3000)
                            );
                        }
                    }, function(){
                        $mdToast.show(
                          $mdToast.simple()
                            .textContent('Ein Fehler tritt auf! Bitte URL überprüfen!')
                            .position("bottom right")
                            .hideDelay(3000)
                        );
                    }
                );
            }
        }
    });
})();