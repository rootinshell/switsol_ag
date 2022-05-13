
frappe.query_reports["Employee Day Report"] = {
    filters: [
        {
            "fieldname":"employee",
            "label": __("Employee"),
            "fieldtype": "Link",
            "options": "Employee",
        },
        {
            "fieldname":"date",
            "label": __("Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
        },
    ],
    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        if(data.type) {
            if(data.type == "pensum" || data.type == "date") {
                var $value = $("<div/>");
                $value.text(data[column.fieldname]);
                $value.css("font-weight", "bold");
                if(column.fieldname == "hours") {
                    $value.css("text-align", "right");
                }
                if(data.holiday && column.fieldname == "hours") {
                    $value.addClass("text-danger");
                }
            }
            if(data.type == "total" && data.future && column.fieldname == "hours") {
                var $value = $(value).addClass("text-primary").css("font-style", "italic");
            } else if(column.fieldname == "workday" && (data.type == "total" || data.type == "delta")) {
                var $value = (column.fieldname == "workday") ? $("<span/>").text(value) : $(value);
                $value.css("font-weight", "bold");
            } else if(data.type == "delta" && column.fieldname!="start" && column.fieldname!="end") {
                var delta = parseFloat(data.hours)
                var css_class = delta > 0 ? "text-success" : "text-danger";
                var $value = $(value).addClass(css_class);
            } 
            if($value) {
                value = $value.wrap("<p></p>").parent().html();
            }
        }
        return value;
    }
}
