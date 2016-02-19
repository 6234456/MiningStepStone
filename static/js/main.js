(function () {

    var app = angular.module('myapp', ['ngMaterial'])
    .controller('AppCtrl', function($scope, $http, $mdToast, $mdDialog) {
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
                if($scope.current.ansprechpartner)
                    $scope.current.ansprechpartner = $scope.current.ansprechpartner.length >0 ? $scope.current.ansprechpartner : tmpAnspr;
                $scope.anspr_disabled = false;
            }
        }
        $scope.jobAnpassen = function(ev){
            //check anrede
            if(!$scope.current.anrede || ($scope.current.anrede && $scope.current.anrede == $scope.anrede[0]) || $scope.current.anrede.trim().length == 0){
                $scope.current.anrede = null;
                $scope.current.ansprechpartner = null;
                $scope.current.ansp_vor = null;
                $scope.current.ansp_nach = null;
            }else{
                if(!$scope.current.ansprechpartner){
                      $mdToast.show(
                          $mdToast.simple()
                            .textContent('Name ist Leer aber mit Anrede! ')
                            .position("bottom right")
                            .hideDelay(3000)
                      );
                    return;
                }

                if($scope.current.ansprechpartner.indexOf("/") !== -1){
                    var tmp = $scope.current.ansprechpartner.split("/")
                    $scope.current.ansp_vor = tmp[0].trim();
                    $scope.current.ansp_nach = tmp[1].trim();
                }else{
                    // without separator but normal 2-part name
                    var tmp = $scope.current.ansprechpartner.split(" ");
                    if(tmp.length == 2){
                        $scope.current.ansp_vor = tmp[0].trim();
                        $scope.current.ansp_nach = tmp[1].trim();
                    }else{
                        $mdToast.show(
                          $mdToast.simple()
                            .textContent('Name ungültig! ' + $scope.current.ansprechpartner)
                            .position("bottom right")
                            .hideDelay(3000)
                        );

                        return;
                    }
                }
            }

            var canceled = true;

            $mdDialog.show(
              $mdDialog.confirm()
                .parent(angular.element(document.querySelector('body')))
                .clickOutsideToClose(true)
                .title('Warnung')
                .textContent('Anpassung wird in Datenbank übernommen.')
                .ok('Los!')
                .cancel('Canel')
                .targetEvent(ev)
            ).then(
                function(){
                    $http({
                              method : "POST",
                              url : "/change",
                              data : "job=" + JSON.stringify($scope.current),
                              headers : {
                                    "Content-Type" : "application/x-www-form-urlencoded"
                              }
                          }
                        ).then(function(response) {
                            refresh();
                            $scope.activeTabNr = 0;
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
            );
        }

        //get bewerbungsstatus
        $http({
                  method : "GET",
                  url : "/status"
              }
            ).then(function(response) {
                $scope.all_status = response.data;
            }
        );

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