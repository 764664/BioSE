/**
 * Created by Jie on 15/10/19.
 */

//var React = require('react');
//var ReactDOM = require('react-dom');

var App = React.createClass({
    getInitialState: function() {
        return {text: '', result: ''};
    },
    handleSubmit: function(e) {
        e.preventDefault();
        waitingDialog.show();
        Controller.loadInitialData(this.state.text);
    },
    onChange: function(e){
        this.setState({text: e.target.value});
    },
    render: function() {
        return (
            <nav className="navbar navbar-default navbar-fixed-top">
                <div className="container">
                <div className="searchfield">
                <form onSubmit={this.handleSubmit}>
                <input onChange={this.onChange} value={this.state.text} />
                <button>Search</button>
                <span id="num_results"></span>
                </form>
                </div>
                </div>
            </nav>
        );
    }
});

var Controller = function(){
    var keyword = '';
    var page = 1;

    return{
        loadData: function() {
            var r = new XMLHttpRequest();
            r.open("GET", "/basic_search/" + keyword + "/" + page, true);
            r.onreadystatechange = function () {
                if (r.readyState != 4 || r.status != 200) return;
                if(r.responseText == '') {
                    ReactDOM.render(<span>No results found.</span>, document.getElementById("num_results"));
                    waitingDialog.hide();
                }
                else {
                    var j = eval(r.responseText);
                    console.info(j);
                    if(!j[0] || j[0].length == 0) {
                        console.info("0 Results Received.")
                    }
                    var alert = ""
                    if (j[2] == 1) {
                        alert = "Failed to fetch data from PubMed."
                    }
                    waitingDialog.hide();
                    ReactDOM.render(<OutPut papers={j[0]} pages={j[1]} current={page} searchid={j[4]} alert={alert}/>, document.getElementById("result"));
                    ReactDOM.render(<span>{j[3]} results found.</span>, document.getElementById("num_results"));
                }
            }.bind(this);
            r.send();
        },
        loadInitialData: function(s) {
            keyword = s;
            this.loadData();
        },
        loadNewPage: function(p) {
            page = p;
            console.info("loadNewPage:" + p);
            this.loadData();
        }
    };
}(jQuery);

var OutPut = React.createClass({
    render: function(){
        return(
            <div>
                <Alerting message={this.props.alert}/>
                <PaperList papers={this.props.papers} searchid={this.props.searchid}/>
                <Pagination pages={this.props.pages} current={this.props.current}/>
            </div>
        )
    }
});

var Alerting = React.createClass({
    render: function(){
        if(this.props.message){
            return(
                <div className="alert alert-warning alert-dismissible" role="alert">
                  <button type="button" className="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>
                  <strong>Warning!</strong> {this.props.message}
                </div>
            )
        }
        else{
            return(<div></div>)
        }

    }
});

var PaperList = React.createClass({
    render: function() {
        var papers = this.props.papers;
        var searchid = this.props.searchid;
        console.info(this.props.searchid);
        if (papers.length > 0) {
            return(
                <div className = "paperlist">
                <ul className="list-group">
                    {
                        papers.map(function (paper) {
                            var citation_url;
                            if(paper["Citations"]) {
                                if(paper["Citations_URL"]) {
                                    citation_url = (
                                    <a href={paper["Citations_URL"]}>
                                    <span className="label label-blue citations">
                                    Citations: {paper["Citations"]}</span></a>
                                    )
                                }
                                else {
                                    citation_url = (
                                    <span className="label label-blue citations">
                                    Citations: {paper["Citations"]}</span>
                                    )
                                }
                            }
                            else {
                                citation_url = (
                                    <span></span>
                                )
                            }
                            return (
                                <li className="list-group-item">
                                    <p><a href={"/jump/" + searchid + "/" + paper["ID"]}><span className="label label-dark title">{paper["Title"]}</span></a></p>
                                    <p><span className="label label-default author">{paper["Author"]}</span></p>
                                    <p className="metainfo">
                                    <span className="label label-info journal">{ paper["Journal"] ? "Journal: " + paper["Journal"] : ""}</span>
                                    <span className="label label-success pubdate">{ paper["PubDate"] ? "PubDate: " + paper["PubDate"] : ""}</span>
                                    <span className="label label-warning score">{ paper["Score"] ? "Score: " + paper["Score"] : ""}</span>
                                    {citation_url}
                                    </p>
                                </li>
                            )
                        })
                    }
                </ul>
                </div>
            )
        }
        else {
            return(
                <p>"No result."</p>
            )
        }

  }
});

var Pagination = React.createClass({
    handleClick: function(event) {
        Controller.loadNewPage(event.currentTarget.dataset.id);
        console.info(event.currentTarget.dataset.id);
    },
    render: function() {
        var pages = this.props.pages;
        var current = this.props.current;
        var display_from = current - 2;
        if((pages <= 5) || (current < 3)) {
            display_from = 1;
        }
        else if(display_from+4 > pages){
            display_from = pages - 4;
        }
        var display_to = display_from + 4;
        var arr = [];
        while(display_from < display_to+1){
            arr.push(display_from++);
        }
        var pageli = function(item, index){
            if(item <= pages) {
                return(<li onClick={this.handleClick} data-id={item} className={(item == current ? "active" : "") + " " + (item > pages ? "disabled" : "")}><a>{item}</a></li>);
            }
            else {
                return(<li data-id={item} className={(item == current ? "active" : "") + " " + (item > pages ? "disabled" : "")}><a>{item}</a></li>);
            }
        }.bind(this);

        if(pages > 0) {
            return(
                <nav className="navbar navbar-default navbar-fixed-bottom">
                    <div className="container mypagination">
                        <nav>
                            <ul className="pagination">
                                <li className={current==1 ? "disabled" : ""} onClick={this.handleClick} data-id={1}>
                                    <a href="#" aria-label="Previous">
                                        <span aria-hidden="true">&laquo;</span>
                                    </a>
                                </li>
                                {
                                    arr.map(pageli)
                                }
                                <li onClick={this.handleClick} data-id={pages}>
                                    <a href="#" aria-label="Next">
                                        <span aria-hidden="true">&raquo;</span>
                                    </a>
                                </li>
                            </ul>
                        </nav>
                    </div>
                </nav>
            )
        }
        else {
            return(
                <div></div>
            )
        }
    }
});

ReactDOM.render(<App />, document.getElementById("form"));

var waitingDialog = waitingDialog || (function ($) {
    'use strict';

    // Creating modal dialog's DOM
    var $dialog = $(
        '<div class="modal fade" data-backdrop="static" data-keyboard="false" tabindex="-1" role="dialog" aria-hidden="true" style="padding-top:15%; overflow-y:visible;">' +
        '<div class="modal-dialog modal-m">' +
        '<div class="modal-content">' +
            '<div class="modal-header"><h3 style="margin:0;"></h3></div>' +
            '<div class="modal-body">' +
                '<div class="progress progress-striped active" style="margin-bottom:0;"><div class="progress-bar" style="width: 100%"></div></div>' +
            '</div>' +
        '</div></div></div>');

    return {
        /**
         * Opens our dialog
         * @param message Custom message
         * @param options Custom options:
         *                options.dialogSize - bootstrap postfix for dialog size, e.g. "sm", "m";
         *                options.progressType - bootstrap postfix for progress bar type, e.g. "success", "warning".
         */
        show: function (message, options) {
            // Assigning defaults
            if (typeof options === 'undefined') {
                options = {};
            }
            if (typeof message === 'undefined') {
                message = 'Loading';
            }
            var settings = $.extend({
                dialogSize: 'm',
                progressType: '',
                onHide: null // This callback runs after the dialog was hidden
            }, options);

            // Configuring dialog
            $dialog.find('.modal-dialog').attr('class', 'modal-dialog').addClass('modal-' + settings.dialogSize);
            $dialog.find('.progress-bar').attr('class', 'progress-bar');
            if (settings.progressType) {
                $dialog.find('.progress-bar').addClass('progress-bar-' + settings.progressType);
            }
            $dialog.find('h3').text(message);
            // Adding callbacks
            if (typeof settings.onHide === 'function') {
                $dialog.off('hidden.bs.modal').on('hidden.bs.modal', function (e) {
                    settings.onHide.call($dialog);
                });
            }
            // Opening dialog
            $dialog.modal();
        },
        /**
         * Closes dialog
         */
        hide: function () {
            $dialog.modal('hide');
        }
    };

})(jQuery);