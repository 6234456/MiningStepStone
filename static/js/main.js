(function () {

    var app = angular.module('myapp', ['ngMaterial'])
    .controller('AppCtrl', function($scope, $http, $mdToast) {
        $scope.anrede = ["N/A","F","M"];
        $scope.anspr_disabled = false;
        $scope.activeTabNr = 0;

        var tmpAnspr = ""

        $scope.checkAnspr = function(){
            if($scope.current.anrede == $scope.anrede[0]){
                tmpAnspr = $scope.current.ansprechpartner;
                $scope.current.ansprechpartner = "";
                $scope.anspr_disabled = true;
            }else{
                $scope.current.ansprechpartner = $scope.current.ansprechpartner.length >0 ? $scope.current.ansprechpartner : tmpAnspr;
                $scope.anspr_disabled = false;
            }
        }

        var refresh = function(){
            $http({
                      method : "GET",
                      url : "/jobs"
                  }
                ).then(function(response) {
                    $scope.data = response.data;
                    var tmp = $scope.data.length;
                    $scope.cnt = tmp === 0?"keine aktive Stelle":tmp === 1 ? "Eine aktive Stelle" : "Insgesamt "+tmp + " Stellen";

                    if(tmp > 0)
                        $scope.current = $scope.data[0];
                    else
                        $scope.current = {};
                }
            );
        }

        refresh();

        $scope.selectItem = function(i){
            $scope.current = $scope.data[i];
            $scope.activeTabNr = 2;
        }


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