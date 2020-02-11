(function (element) {
    element.matches = element.matches || element.mozMatchesSelector || element.msMatchesSelector || element.oMatchesSelector || element.webkitMatchesSelector;
    element.closest = element.closest || function closest(selector) {
        if (!this || !this.parentElement && !this.matches(selector)) return null;
        else if (this.matches(selector)) return this;
        else return this.parentElement.closest(selector);
    };
}(Element.prototype));

function setDropdown() {
    var list = document.querySelectorAll(".dropdown-select:not(.created)");
    for (var sel in list)
        if (list.hasOwnProperty(sel))
            createDropdown(list[sel]);

    function createDropdown(select) {
        var searchDisable = select.dataset["searchdisable"];
        var placeholder = select.dataset["placeholder"];
        var opened = select.dataset["opened"];
        var div = createElement("div", "div", select.parentNode, null);
        var dropdown = createElement("div", "dropdown" + (opened != null && opened == "true" ? " open" : ""), div,
            opened == null || opened != "true" ? { "click": openSelect, "blur": openSelect } : null);
        dropdown.select = select;
        dropdown.setAttribute("tabindex", "0");
        if (opened == null || opened != "true")
            createElement("div", "selected", dropdown, null);
        if (searchDisable == null || searchDisable != "true") {
            var search = createElement("div", "fstsearch", dropdown, null);
            var e = { "keyup": getSearch, "paste": getSearch };
            if (opened == null || opened != "true") e["blur"] = openSelect;
            createElement("input", "searchinput", search, e).placeholder = placeholder != undefined ? placeholder : "";
        }
        if (select.multiple) {
            var selectAll = createElement("button", "all", dropdown, { "click": selectAllOptions });
            selectAll.textContent = "Select All";
            selectAll.type = "button";
            selectAll.selected = false;
        }
        createElement("div", "list", dropdown, null);
        select.dropdown = { dd: dropdown, rebind: function () { rebindDropdown(select); } };
        rebindDropdown(select);
        select.classList.add("created");
    }

    function openSelect(event, open, force) {
        var select = event.target.classList.contains("dropdown") ? event.target.select : event.target.closest(".dropdown").select;
        open = open == null ? event.type != "blur" : open;
        var el = select.dropdown.dd;
        if (checkEvent(event, force)) return;
        if (!open || el.classList.contains("open")) {
            el.classList.remove("open");
            el.parentNode.classList.remove("open");
            return;
        }
        el.classList.add("open");
        el.parentNode.classList.add("open");
        if(select.dataset["searchdisable"] == null && select.dataset["searchdisable"] != "true")
            el.querySelector(".searchinput").focus();
    }

    function checkEvent(event, force) {
        return event.relatedTarget != null && (event.relatedTarget.tagName == "INPUT" || (event.relatedTarget.tagName == "BUTTON" && force == undefined))
            || event.target.tagName == "INPUT" && event.type != "blur"
            || event.target.tagName == "INPUT" && (event.relatedTarget != null && event.relatedTarget.className == "dropdown open")
            || event.target.classList.contains("selected") && event.type == "blur" && document.activeElement.classList.contains("searchinput")
            || event.type == "blur" && (document.activeElement.className == "list" || document.activeElement.className == "all")
            || event.target.tagName == "BUTTON" && force == undefined;
    }

    function changeSelect(event) {
        var select = event.target.closest(".dropdown").select;
        var dd = select.dropdown.dd;
        var selectAll = dd.querySelector(".all");
        var opened = select.dataset["opened"] == null || select.dataset["opened"] != "true";
        if (select.value != event.target.dataset["value"] && !select.multiple) {
            select.value = event.target.dataset["value"];
            if (dd.querySelector(".list>.selected") != null)
                dd.querySelector(".list>.selected").classList.remove("selected");
            event.target.classList.add("selected");
            if (opened)
                dd.querySelector(".selected").textContent = event.target.textContent;
            initEvent("change", select);
        }
        if (select.multiple) {
            changeMultipleSelect(select, event, dd, selectAll, opened);
        }
        if (opened)
            openSelect(event, false);
    }

    function changeMultipleSelect(select, event, dd, selectAll, opened) {
        select.querySelector("[value='" + event.target.dataset["value"] + "']").selected = !event.target.classList.contains("selected");
        if (event.target.classList.contains("selected"))
            event.target.classList.remove("selected");
        else
            event.target.classList.add("selected");
        initEvent("change", select);
        var length = dd.querySelectorAll(".list>.selected").length;
        selectAll.selected = length > 0;
        if (opened)
            dd.querySelector(".selected").textContent = length == 1 ? event.target.textContent : length + " options selected";
        selectAll.textContent = selectAll.selected ? "Deselect All" : "Select All";
    }

    function rebindDropdown(select) {
        var optList = select.querySelectorAll("option");
        var ddList = select.dropdown.dd.querySelector(".list");
        while (ddList.lastChild)
            ddList.removeChild(ddList.lastChild);
        for (var opt in optList) {
            if (optList.hasOwnProperty(opt)) {
                var listEl = document.createElement("div");
                listEl.textContent = optList[opt].text;
                listEl.dataset["value"] = optList[opt].value;
                if (optList[opt].selected)
                    listEl.classList.add("selected");
                listEl.addEventListener("click", changeSelect);
                ddList.appendChild(listEl);
            }
        }
        setHeader(select, null);
    }

    function initEvent(eventName, target) {
        var event;
        if (typeof (Event) === "function")
            event = new Event(eventName, { bubbles: true });
        else {
            event = document.createEvent("Event");
            event.initEvent(eventName, true, true);
        }
        target.dispatchEvent(event);
    }

    function getSearch(event) {
        var pasteText = event.type != "paste" ? "" : typeof event.clipboardData === "undefined" ?
            window.clipboardData.getData("Text") : event.clipboardData.getData("text/plain");
        var val = event.type != "paste" ? event.target.value : pasteText;
        var dd = event.target.closest(".dropdown");
        var ddList = dd.querySelectorAll(".list>div");
        for (var div in ddList)
            if (ddList.hasOwnProperty(div))
                if (ddList[div].textContent.trim().toLowerCase().indexOf(val.trim().toLowerCase()) != -1)
                    ddList[div].classList.remove("hideFst");
                else
                    ddList[div].classList.add("hideFst");
    }

    function createElement(type, className, parent, eventListener) {
        var element = document.createElement(type);
        if (className != null)
            for (var c in className.split(" "))
                if (!isNaN(c))
                    element.classList.add(className.split(" ")[c]);
        if (eventListener != null)
            for (var ev in eventListener)
                if (eventListener.hasOwnProperty(ev))
                    element.addEventListener(ev, eventListener[ev], true);
        parent.appendChild(element);
        return element;
    }

    function selectAllOptions(event) {
        var select = event.target.closest(".dropdown").select;
        var dd = select.dropdown.dd;
        var selected = !event.target.selected;
        event.target.selected = selected;
        var list = !selected ? dd.querySelectorAll(".selected") : dd.querySelectorAll(".list>div:not(.hideFst)");
        for (var l in list)
            if (list.hasOwnProperty(l)) {
                select.querySelector("[value='" + list[l].dataset["value"] + "']").selected = selected;
                if (selected)
                    list[l].classList.add("selected");
                else
                    list[l].classList.remove("selected");
            }
        initEvent("change", select);
        event.target.textContent = !selected ? "Select All" : "Deselect All";
        setHeader(select, event);
    }

    function setHeader(select, event) {
        if (select.dataset["opened"] == null || select.dataset["opened"] != "true") {
            var text = "";
            var sOption = select.options[select.selectedIndex];
            if (select.multiple) {
                var count = 0;
                for (var s in select.options)
                    if (select.options.hasOwnProperty(s) && select.options[s].selected == true)
                        count++;
                text = count == 1 ? sOption.text : count + " options selected";
            }
            select.dropdown.dd.querySelector(".selected").textContent = select.multiple ? text : sOption != undefined ? sOption.text : "";
            if(event != null)
                openSelect(event, false, true);
        }
    }
}

document.addEventListener("DOMContentLoaded", setDropdown);
