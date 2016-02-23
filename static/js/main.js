(function () {

    var app = angular.module('myapp', ['ngMaterial'])
    .controller('AppCtrl', function($scope, $http, $mdToast, $mdDialog, $filter) {
        $scope.anrede = ["N/A","F","M"];
        $scope.anspr_disabled = false;
        $scope.activeTabNr = 0;
        $scope.sortOrder = true;

        $scope.updateSearchCnt = function(){
            var tmp = $scope.filtered.length;
            $scope.data = $scope.filtered;
            $scope.cnt = tmp === 0?"keine aktive Stelle":tmp === 1 ? "Eine aktive Stelle" : "Insgesamt "+tmp + " Stellen";
        };

        $scope.resetSearch = function(){
            $scope.data = $scope.dataBackup;
            $scope.searchKey = "";
            $scope.cnt = $scope.cntBackup;
        }

        $scope.mySort = function(){
            $scope.sortOrder = !$scope.sortOrder;
            $scope.data = $filter('orderBy')($scope.data, "bewertung", $scope.sortOrder);
        }

        $scope.mySortTime = function(){
            $scope.sortOrder = !$scope.sortOrder;
            $scope.data = $filter('orderBy')($scope.data, "eingetragen_am", $scope.sortOrder);
        }

        var tmpAnspr = ""

        $scope.chooseProgrBarClass = function(i){
            if(i <= 40)
                return "md-accent";

            if(i <= 75)
                return "md-warn";

            return "md-primary";
        }

        $scope.deleteItem = function(i){
            $mdDialog.show(
              $mdDialog.confirm()
                .parent(angular.element(document.querySelector('body')))
                .clickOutsideToClose(true)
                .title('Warnung')
                .textContent('Die Eingabe zu löschen?')
                .ok('OK')
                .cancel('Canel')
//                .targetEvent(ev)
            ).then(
                function(){
                    $http({
                              method : "POST",
                              url : "/delete",
                              data : JSON.stringify({targ: $scope.data[i].id}),
                              headers : {
                                    "Content-Type" : "application/json"
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
                                .textContent('Ein Fehler tritt auf! Löschen ohne Erfolg.')
                                .position("bottom right")
                                .hideDelay(3000)
                            );
                        }
                    );
                }
            );
        }

        $scope.email = function(ev){

            if(!$scope.current.durch_email){
                $mdDialog.show(
                  $mdDialog.confirm()
                    .parent(angular.element(document.querySelector('body')))
                    .clickOutsideToClose(true)
                    .title('Warnung')
                    .textContent('Email-Feld zu aktivieren?')
                    .ok('OK')
                    .cancel('Canel')
                ).then(
                    function(){
                        $scope.current.durch_email = true;
                        $scope.email_status = "Direkt zumailen";
                    }
                );

                return ;
            }


            $mdDialog.show(
              $mdDialog.confirm()
                .parent(angular.element(document.querySelector('body')))
                .clickOutsideToClose(true)
                .title('Warnung')
                .textContent('Nicht gespeicherte Anpassungen gehen verloren.')
                .ok('Los!')
                .cancel('Canel')
                .targetEvent(ev)
            ).then(
                function(){
                    var cancel = false;

                    if($scope.current.status_id !== 100){
                        $mdDialog.show(
                          $mdDialog.confirm()
                            .parent(angular.element(document.querySelector('body')))
                            .clickOutsideToClose(true)
                            .title('Warnung')
                            .textContent('Du hast dich bereits darum beworben.Nochmal?')
                            .ok('Ja!')
                            .cancel('Canel')
                            .targetEvent(ev)
                        ).then(null, function(){
                            cancel = true;
                        })
                    }

                    if(! cancel){
                        $http({
                                 method : "POST",
                                 url : "/send",
                                 data : JSON.stringify({targ: $scope.current.id}),
                                 headers : {
                                       "Content-Type" : "application/json"
                                 }
                             }
                           ).then(function(response) {
                               if(response.data.trim() == "OK"){
                                   refresh($scope.currentIndex);
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
                                   .textContent('Ein Fehler tritt auf!')
                                   .position("bottom right")
                                   .hideDelay(3000)
                               );
                           }
                        );
                    }
                }
            );
       }

        $scope.doku = function(ev){
            $http({
                      method : "POST",
                      url : "/doku",
                      data : JSON.stringify({targ: $scope.current.id}),
                      headers : {
                            "Content-Type" : "application/json"
                      }
                  }
                ).then(function(response) {
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
                        .textContent('Ein Fehler tritt auf!')
                        .position("bottom right")
                        .hideDelay(3000)
                    );
                }
            );
        }

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
                    var tmpHasKey = $scope.current['$$hashKey'];
                    delete $scope.current['$$hashKey'];

                    $http({
                              method : "POST",
                              url : "/change",
                              data : JSON.stringify($scope.current),
                              headers : {
                                    "Content-Type" : "application/json"
                              }
                          }
                        ).then(function(response) {
//                            refresh($scope.currentIndex);
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

                    $scope.current['$$hashKey'] = tmpHasKey;
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

        var refresh = function(idx){
            idx = idx || 0;

            $http({
                      method : "GET",
                      url : "/jobs"
                  }
                ).then(function(response) {
                    $scope.data = response.data;
                    $scope.dataBackup = response.data;
                    var tmp = $scope.data.length;
                    $scope.cnt = tmp === 0?"keine aktive Stelle":tmp === 1 ? "Eine aktive Stelle" : "Insgesamt "+tmp + " Stellen";
                    $scope.cntBackup = $scope.cnt;
                    if(tmp > 0){
                        $scope.current = $scope.data[idx];
                        $scope.email_status = $scope.current.durch_email ? "Direkt zumailen" : "Email Aktivieren";
                    }
                    else
                        $scope.current = {};
                }
            );
        }

        refresh();

        $scope.selectItem = function(i){
            $scope.current = $scope.data[i];
            $scope.activeTabNr = 2;
            $scope.currentIndex = i;
            $scope.email_status = $scope.current.durch_email ? "Direkt zumailen" : "Email Aktivieren";
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