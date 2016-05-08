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
        self.connection = parameters[1];

        PNotify.prototype.options.confirm.buttons= [];
        self.timeoutOnePopupText = gettext('Powering off in ');
        self.timeoutOnePopupOptions = {
            title: gettext('Power off relay 1'),
            type: 'notice',
            icon: true,
            hide: false,
            confirm: {
                confirm: true,
                buttons: [{
                    text: 'Cancel',
                    addClass: 'btn-block btn-danger',
                    promptTrigger: true,
                    click: function(notice, value){
                        notice.remove();
                        notice.get().trigger("pnotify.cancel", [notice, value]);
                    }
                }]
            },
            buttons: {
                closer: false,
                sticker: false,
            },
            history: {
                history: false
            }
        };

        self.timeoutTwoPopupText = gettext('Powering off in ');
        self.timeoutTwoPopupOptions = {
            title: gettext('Power off relay 2'),
            type: 'notice',
            icon: true,
            hide: false,
            confirm: {
                confirm: true,
                buttons: [{
                    text: 'Cancel',
                    addClass: 'btn-block btn-danger',
                    promptTrigger: true,
                    click: function(notice, value){
                        notice.remove();
                        notice.get().trigger("pnotify.cancel", [notice, value]);
                    }
                }]
            },
            buttons: {
                closer: false,
                sticker: false,
            },
            history: {
                history: false
            }
        };

        self.cooldownOnePopupText = gettext('Waiting for cooldown ');
        self.cooldownOnePopupOptions = {
            title: gettext('Power off relay 1'),
            type: 'notice',
            icon: true,
            hide: false,
            confirm: {
                confirm: true,
                buttons: [{
                    text: 'Cancel',
                    addClass: 'btn-block btn-danger',
                    promptTrigger: true,
                    click: function(notice, value){
                        notice.remove();
                        notice.get().trigger("pnotify.cancel", [notice, value]);
                    }
                }]
            },
            buttons: {
                closer: false,
                sticker: false,
            },
            history: {
                history: false
            }
        };

        self.cooldownTwoPopupText = gettext('Waiting for cooldown ');
        self.cooldownTwoPopupOptions = {
            title: gettext('Power off relay 2'),
            type: 'notice',
            icon: true,
            hide: false,
            confirm: {
                confirm: true,
                buttons: [{
                    text: 'Cancel',
                    addClass: 'btn-block btn-danger',
                    promptTrigger: true,
                    click: function(notice, value){
                        notice.remove();
                        notice.get().trigger("pnotify.cancel", [notice, value]);
                    }
                }]
            },
            buttons: {
                closer: false,
                sticker: false,
            },
            history: {
                history: false
            }
        };

        self.rOneName = ko.observable();
        self.rOneShow = ko.observable(false);
        self.rTwoName = ko.observable();
        self.rTwoShow = ko.observable(false);

        self.onBeforeBinding = function() {
        };

        self.isConnected = ko.computed(function() {
            return self.connection.loginState.isUser();
        });

        self.initButtons = function(data) {
            self.rOneName(data.rOneName);
            self.rOneShow(data.rOneShow);
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

            if (data.type == "timeoutOne") {
                if (data.timeout_value > 0) {
                    self.timeoutOnePopupOptions.text = self.timeoutOnePopupText + data.timeout_value;
                    if (self.timeoutOnePopup !== undefined) {
                        self.timeoutOnePopup.update(self.timeoutOnePopupOptions);
                    } else {
                        self.timeoutOnePopup = new PNotify(self.timeoutOnePopupOptions);
                        self.timeoutOnePopup.get().on('pnotify.cancel', function() {self.cancelPwrOffRelayOne(true);});
                    }
                } else {
                    self.timeoutOnePopup.remove();
                    self.timeoutOnePopup = undefined;
                }
            } else if (data.type == "timeoutTwo") {
                if (data.timeout_value > 0) {
                    self.timeoutTwoPopupOptions.text = self.timeoutTwoPopupText + data.timeout_value;
                    if (self.timeoutTwoPopup !== undefined) {
                        self.timeoutTwoPopup.update(self.timeoutTwoPopupOptions);
                    } else {
                        self.timeoutTwoPopup = new PNotify(self.timeoutTwoPopupOptions);
                        self.timeoutTwoPopup.get().on('pnotify.cancel', function() {self.cancelPwrOffRelayTwo(true);});
                    }
                } else {
                    self.timeoutTwoPopup.remove();
                    self.timeoutTwoPopup = undefined;
                }
            } else if (data.type == "cooldownOne") {
                if (data.timeout_value > 0) {
                    self.cooldownOnePopupOptions.text = self.cooldownOnePopupText + data.timeout_value;
                    if (self.cooldownOnePopup !== undefined) {
                        self.cooldownOnePopup.update(self.cooldownOnePopupOptions);
                    } else {
                        self.cooldownOnePopup = new PNotify(self.cooldownOnePopupOptions);
                        self.cooldownOnePopup.get().on('pnotify.cancel', function() {self.cancelCooldownPwrOffRelayOne(true);});
                    }
                } else {
                    self.cooldownOnePopup.remove();
                    self.cooldownOnePopup = undefined;
                }
            } else if (data.type == "cooldownTwo") {
                if (data.timeout_value > 0) {
                    self.cooldownTwoPopupOptions.text = self.cooldownTwoPopupText + data.timeout_value;
                    if (self.cooldownTwoPopup !== undefined) {
                        self.cooldownTwoPopup.update(self.cooldownTwoPopupOptions);
                    } else {
                        self.cooldownTwoPopup = new PNotify(self.cooldownTwoPopupOptions);
                        self.cooldownTwoPopup.get().on('pnotify.cancel', function() {self.cancelCooldownPwrOffRelayTwo(true);});
                    }
                } else {
                    self.timeoutTwoPopup.remove();
                    self.timeoutTwoPopup = undefined;
                }
            } else {
                self.rOneName(data.rOneName);
                self.rOneShow(data.rOneShow);
                self.rTwoName(data.rTwoName);
                self.rTwoShow(data.rTwoShow);
            }
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

        self.cancelPwrOffRelayOne = function(cancelValue) {
            self.timeoutOnePopup.remove();
            self.timeoutOnePopup = undefined;
            $.ajax({
                url: API_BASEURL + "plugin/powercontrol",
                type: "POST",
                dataType: "json",
                data: JSON.stringify({
                    command: "cancelOne"
                }),
                contentType: "application/json; charset=UTF-8"
            })
        }

        self.cancelCooldownPwrOffRelayOne = function(cancelValue) {
            self.cooldownOnePopup.remove();
            self.cooldownOnePopup = undefined;
            $.ajax({
                url: API_BASEURL + "plugin/powercontrol",
                type: "POST",
                dataType: "json",
                data: JSON.stringify({
                    command: "cancelCooldownOne"
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

        self.cancelPwrOffRelayTwo = function(cancelValue) {
            self.timeoutTwoPopup.remove();
            self.timeoutTwoPopup = undefined;
            $.ajax({
                url: API_BASEURL + "plugin/powercontrol",
                type: "POST",
                dataType: "json",
                data: JSON.stringify({
                    command: "cancelTwo"
                }),
                contentType: "application/json; charset=UTF-8"
            })
        }
    }

    self.cancelCooldownPwrTwoRelayOne = function(cancelValue) {
            self.cooldownTwoPopup.remove();
            self.cooldownTwoPopup = undefined;
            $.ajax({
                url: API_BASEURL + "plugin/powercontrol",
                type: "POST",
                dataType: "json",
                data: JSON.stringify({
                    command: "cancelCooldownTwo"
                }),
                contentType: "application/json; charset=UTF-8"
            })
        }

    ADDITIONAL_VIEWMODELS.push([
        PowercontrolViewModel,
        ["settingsViewModel","connectionViewModel"],
        ["#powercontrol"]
    ]);
});
