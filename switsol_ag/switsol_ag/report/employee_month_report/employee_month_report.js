frappe.provide("switsol_ag.employee_month_report");

switsol_ag.employee_month_report = {
    filters: [
        {
            "fieldname": "employee",
            "label": __("Employee"),
            "fieldtype": "Link",
            "options": "Employee",
        },
        {
            "fieldname": "month",
            "label": __("Month"),
            "fieldtype": "Select",
            "options": "Jan\nFeb\nMar\nApr\nMay\nJun\nJul\nAug\nSep\nOct\nNov\nDec",
            "default": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][
                frappe.datetime.str_to_obj(frappe.datetime.get_today()).getMonth()],
        },
        {
            "fieldname": "fiscal_year",
            "label": __("Fiscal Year"),
            "fieldtype": "Link",
            "options": "Fiscal Year",
            "default": frappe.sys_defaults.fiscal_year
        }
    ],
    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if(data.type && column.fieldname != "delta" &&
            (data.type == "pensum" || data.type == "total")) {
            var $value = (column.fieldname == "date") ? $("<span/>").text(value) : $(value);
            $value.css("font-weight", "bold");
            value = $value.wrap("<p></p>").parent().html();
        }

        if(column.fieldname == "date" && data.is_holiday) {
            var $value = $("<span/>").addClass("text-danger").text(value)
            value = $value.wrap("<p></p>").parent().html();
        }

        if(column.fieldname == "delta" && data.delta) {
            var delta = parseFloat(data.delta)
            var css_class = delta > 0 ? "text-success" : "text-danger";
            var $value = $("<span/>").addClass(css_class).text(value)
            value = $value.wrap("<p></p>").parent().html();
        }

        if(column.fieldname == "total") {
            if(data.future) {
                var $value = $(value).addClass("text-primary").css("font-style", "italic");
                value = $value.wrap("<p></p>").parent().html();
            } else if(data.type != "total"){
                value = repl("<a onclick='switsol_ag.employee_month_report.show_day_report(\"%(employee)s\", \"%(date)s\")'>\
                    %(value)s</a>", {employee: data.employee,
                                     date: data.date_object,
                                     value: value});
            }
        }

        return value;
    },

    show_day_report: function(employee, date) {
        frappe.route_options = {
            employee: employee,
            date: date
        };
        frappe.set_route("query-report", "Employee Day Report");
    }
}

frappe.query_reports["Employee Month Report"] = switsol_ag.employee_month_report;
