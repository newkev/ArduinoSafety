
$(function() {

    function CostEstimationViewModel(parameters) {
        var self = this;

        self.printerState = parameters[0];
        self.settings = parameters[1];
        self.loginState = parameters[2];
        self.filamentManager = parameters[3];

     
        self.estimatedCostString = ko.pureComputed(function() {
            var pluginSettings = self.settings.settings.plugins.arduinosafety;
            var jobFilament =  self.printerState.filament();

            // calculating electricity cost
            var powerConsumption = parseFloat(pluginSettings.powerConsumption());

            var costPerHour = powerConsumption * costOfElectricity;

            return 100;
        });

        self.onBeforeBinding = function() {
            var element = $("#state").find("hr:nth-of-type(2)");
            if (element.length) {
                var name = gettext("Cost");
                var text = gettext("Estimated print cost based on required quantity of filament and print time");
                element.before("<div id='costestimation_string' data-bind='visible: showEstimatedCost()'><span title='" + text + "'>" + name + "</span>: <strong data-bind='text: estimatedCostString'></strong></div>");
            }
        };
    }

    OCTOPRINT_VIEWMODELS.push({
        construct: CostEstimationViewModel,
        dependencies: ["printerStateViewModel", "settingsViewModel",
                       "loginStateViewModel", "filamentManagerViewModel"],
        optional: ["filamentManagerViewModel"],
        elements: ["#costestimation_string", "#settings_plugin_arduinosafety"]
    });
});