/*
 * View model for OctoPrint-Powercontrol
 *
 * Author: Daniel Konrad / IT4Race GmbH
 * License: AGPLv3
 */
$(function() {
    function PowercontrolViewModel(parameters) {
        var self = this;

        self.settings = parameters[0];

        self.rOneName = ko.observable();
        self.rOneShow = ko.observable(false);
        self.rTwoName = ko.observable();
        self.rTwoShow = ko.observable(false);

        self.initButtons = function(data) {
            self.rOneName(data.rOneName);
            self.rOneShow(data.rOneShow)
            self.rTwoName(data.rTwoName);
            self.rTwoShow(data.rTwoShow);
        };

        self.onStartupComplete = function() {
            // WebApp started, get buttons
            $.ajax({
                url: API_BASEURL + "plugin/powercontrol",
                type: "GET",
                dataType: "json",
                success: self.initButtons
            });
        }

        self.onDataUpdaterPluginMessage = function(plugin, data) {
            if (plugin != "powercontrol") {
                return;
            }

            self.rOneName(data.rOneName);
            self.rOneShow(data.rOneShow);
            self.rTwoName(data.rTwoName);
            self.rTwoShow(data.rTwoShow);
        };

        self.pwrOnRelayOne = function() {
            // Power on relay one button was pressed
            $.ajax({
                url: API_BASEURL + "plugin/powercontrol",
                type: "POST",
                dataType: "json",
                data: JSON.stringify({
                    command: "pwrOnRelayOne"
                }),
                contentType: "application/json; charset=UTF-8"
            })
        }

        self.pwrOffRelayOne = function() {
            // Power off relay one button was pressed
            $.ajax({
                url: API_BASEURL + "plugin/powercontrol",
                type: "POST",
                dataType: "json",
                data: JSON.stringify({
                    command: "pwrOffRelayOne"
                }),
                contentType: "application/json; charset=UTF-8"
            })
        }

        self.pwrOnRelayTwo = function() {
            // Power on relay two button was pressed
            $.ajax({
                url: API_BASEURL + "plugin/powercontrol",
                type: "POST",
                dataType: "json",
                data: JSON.stringify({
                    command: "pwrOnRelayTwo"
                }),
                contentType: "application/json; charset=UTF-8"
            })
        }

        self.pwrOffRelayTwo = function() {
            // Power off relay two button was pressed
            $.ajax({
                url: API_BASEURL + "plugin/powercontrol",
                type: "POST",
                dataType: "json",
                data: JSON.stringify({
                    command: "pwrOffRelayTwo"
                }),
                contentType: "application/json; charset=UTF-8"
            })
        }

    }

    ADDITIONAL_VIEWMODELS.push([
        PowercontrolViewModel,
        ["settingsViewModel"],
        ["#powercontrol"]
    ]);
});
