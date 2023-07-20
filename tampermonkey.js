// ==UserScript==
// @name         JobCollector
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  try to take over the world!
// @author       You
// @match        https://www.stepstone.de/stellenangebote*
// @grant        GM_registerMenuCommand
// @grant        GM_setClipboard
// ==/UserScript==

(function() {
    'use strict';

    function removeQueryStr(url) {
        const urlObj = new URL(url);

        urlObj.search = '';

        return urlObj.toString();

    }

    function test() {

        const url_ag = document.querySelector('[data-at="lccp-companycard-company-btn"]');
        const ap = document.querySelector(".at-recruiter-name");
        const contact = __PRELOADED_STATE__.ContentBlock.textSectionsData.filter(e=>e.type == "contact")[0].content;
        const email = contact.match(/"mailto:(.+?)"/)?.[1];

        const ansprechpartner = !!ap?ap.innerText:null
        let mapping = {
            url: removeQueryStr(window.location.toString()),
            job: document.querySelector('[data-at="header-job-title"]').textContent,
            jobID: window.location.toString().match(/\d{7,}/)[0],
            arbeitgeber: (document.querySelector('[data-at="address-head"]') || document.querySelector('[data-at="header-company-name"]')).textContent,
            ansprechpartner : ansprechpartner,
            email: email,
            plz: null,
            stadt: null,
            strasse: null,
            anrede: null,
            eintrittstermin: true,
            gehaltsvorstellung: true,
            istDurchEmail: email === null,
            agID: document.querySelector('[data-at="lccp-companycard-logo-link"]')?.getAttribute("href")?.match(/-(\d{6,})\//)?.[1]
        };


// .replace(/<\/?[^>]+(>|$)/g, "/n")
        const arr = contact.replace(/<\/?[^>]+(>|$)/g, "/n").split("/n").map(e=>e.trim()).filter(e=>e.length>0);

        arr.forEach((e,i)=>{
            if(!mapping.plz){
                const plz = e.match(/\d{5}/)?.[0]
                if(plz){
                    mapping.plz = plz
                    mapping.stadt = e.slice(e.indexOf(plz) + 6)
                    if(i > 0) mapping.strasse = arr[i-1]

                }
            }

            if(!mapping.ansprechpartner){
                if(e.match(/(Mr)|(Herr)/)){
                    mapping.anrede = "M";
                    mapping.ansprechpartner = e.split(" ").slice(1).join(" ");
                } else if(e.match(/(Ms)|(Frau)/)){
                    mapping.anrede = "F";
                    mapping.ansprechpartner = e.split(" ").slice(1).join(" ");
                }

            }



        })






        if(!url_ag){
            // data-at="address-text"
            const address = document.querySelector('[data-at="address-text"]')
            if(address){
                const text = address.textContent.split(",").map(e=>e.trim());
                if(text.length == 3){
                    const plz = text[1].match(/\d{5}/)?.[0];
                    mapping = {
                        ...mapping,
                        strasse: text[0],
                        plz: plz,
                        stadt: text[1].slice(text[1].indexOf(plz) + 6)
                    }
                }
            }

            GM_setClipboard(JSON.stringify(mapping));
            // window.alert("done");




        }else{

            fetch(url_ag.getAttribute("href")).then(e=>e.text()).then(e=>{

                //console.log(new DOMParser().parseFromString(e, 'text/html').body.querySelector('[data-block="app-inShort"]').getAttribute("data-initialdata"));
                const doc = new DOMParser().parseFromString(e, 'text/html').body;

                const ag = JSON.parse(doc.querySelector('[data-block="app-inShort"]').getAttribute("data-initialdata"));

                // data-companyid

                mapping = {
                    ...mapping,
                    strasse: ag.street + " " + ag.streetNumber,
                    stadt: ag.city,
                    plz: ag.postalCode,
                    agID: doc.querySelector('[data-companyid]').getAttribute("data-companyid"),
                }


                GM_setClipboard(JSON.stringify(mapping));
                //window.alert("done");


            })

        }



    }

    GM_registerMenuCommand("点我收集", test, "e");

    // Your code here...
})();