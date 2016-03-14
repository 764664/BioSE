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
        //waitingDialog.show();
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
                <form id="form_search" className="navbar-form" onSubmit={this.handleSubmit}>
                <input className="form-control" onChange={this.onChange} value={this.state.text} placeholder="Search"/>
                <button className="btn btn-primary" id="search_button">Search</button>
                </form>
                <span id="span_num_results"></span>
                <span id="span_order_by"></span>
                </div>
                </div>
            </nav>
        );
    }
});

var Controller = function(){
    var keyword = '';
    var page = 1;
    var order_by = "Default";
    var filter_by = "Default";

    return{
        loadData: function() {
            $('.modal').modal('toggle');
            var xmlhttp = new XMLHttpRequest();
            xmlhttp.timeout = 30000;
            var url = "/search/" + keyword + "?page=" + page + "&order_by=" + order_by + "&filter_by=" + filter_by;
            xmlhttp.open("GET", url, true);
            //r.onreadystatechange = function () {
            xmlhttp.onload = function () {
                //if (xmlhttp.readyState != 4 || xmlhttp.status != 200) return;
                var j = JSON.parse(xmlhttp.responseText);
                console.info(j);
                //if(!j[0] || j[0].length == 0) {
                //    console.info("0 Results Received.")
                //}
                //var alert = ""
                //if (j[2] == 1) {
                //    alert = "Failed to fetch data from PubMed."
                //}
                //waitingDialog.hide();
                $('.modal').modal('toggle');
                ReactDOM.render(<OutPut papers={j["result"]} pages={j["result_info"]["page"]} current={page} searchid={j["result_info"]["id"]} alert=""/>, document.getElementById("result"));
                ReactDOM.render(<span className="navbar-text">{j["result_info"]["count"] +" results found."}</span>, document.getElementById("span_num_results"));
                ReactDOM.render(<OrderBy />, document.getElementById("span_order_by"))
            }.bind(this);
            xmlhttp.ontimeout = function(){
                console.info("AJAX Timeout.");
                ReactDOM.render(<span>AJAX Timeout.</span>, document.getElementById("num_results"));
                $('.modal').modal('toggle');
            };
            xmlhttp.onerror = function () {
                console.info("AJAX Error.");
                ReactDOM.render(<span>AJAX Error.</span>, document.getElementById("num_results"));
                $('.modal').modal('toggle');
            };
            xmlhttp.send();
        },
        loadInitialData: function(p_keyword=keyword, p_page=1, p_order_by="Default", p_filter_by="Default") {
            keyword = p_keyword;
            page = p_page;
            order_by = p_order_by;
            filter_by = p_filter_by;
            this.loadData();
        },
        loadNewPage: function(p) {
            page = p;
            console.info("loadNewPage:" + p);
            this.loadData();
        }
    };
}();

var OrderBy = React.createClass({
    handleClick: function(e){
        e.preventDefault();
        // console.info(e.target.text);
        Controller.loadInitialData(undefined, 1, e.target.text);
    },
    render: function(){
        return(
            <div className="btn-group navbar-btn" id="order_by">
              <button type="button" className="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                Order By <span className="caret"></span>
              </button>
              <ul className="dropdown-menu">
                <li><a onClick={this.handleClick} href="#">Default</a></li>
                <li role="separator" className="divider"></li>
                <li><a onClick={this.handleClick} href="#">Publication Date(Ascending)</a></li>
                <li><a onClick={this.handleClick} href="#">Publication Date(Descending)</a></li>
              </ul>
            </div>
            )
    }
});

var FilterBy = React.createClass({
    handleClick: function(e){
        e.preventDefault();
        // console.info(e.target.text);
        Controller.loadInitialData(undefined, 1, e.target.text);
    },
    render: function(){
        return(
            <div className="btn-group navbar-btn" id="order_by">
              <button type="button" className="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                Order By <span className="caret"></span>
              </button>
              <ul className="dropdown-menu">
                <li><a onClick={this.handleClick} href="#">Default</a></li>
                <li role="separator" className="divider"></li>
                <li><a onClick={this.handleClick} href="#">Publication Date(Ascending)</a></li>
                <li><a onClick={this.handleClick} href="#">Publication Date(Descending)</a></li>
              </ul>
            </div>
            )
    }
});

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

var Detail = React.createClass({
    render: function() {
        return(
            <div className="detail">
                <a href={"/jump/" + this.props.searchid + "/" + this.props.paper["ID"]}>
                    {this.props.paper["Title"]}
                </a>
                <pre>
                    { this.props.content }
                </pre>
            </div>
        )
    }
});

var Paper = React.createClass({
    getInitialState: function(){
        return {
            selected: '',
            detail: ''
        }
    },
    showDetails: function(e) {
        e.preventDefault();

        var searchid = this.props.searchid;
        var paper = this.props.paper;
        var id = paper["PMID"];

        var xmlhttp = new XMLHttpRequest();
        var url = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=" + id + "&rettype=abstract&retmode=text";
        //
        //if(document.getElementById("detail"+id).hasChildNodes()) {
        //    var detailDOM = document.getElementById("detail"+id).firstChild;
        //    if (detailDOM.style.display !== 'none') {
        //        detailDOM.style.display = 'none';
        //    }
        //    else{
        //        detailDOM.style.display = 'block';
        //    }
        //
        //    if(document.getElementById("detail"+id).firstChild.style.display !== 'none'){
        //        document.getElementById("h"+id).style.fontSize = '20px';
        //    }
        //    else{
        //        document.getElementById("h"+id).style.fontSize = '14px';
        //    }
        //}
        //else{
        //    xmlhttp.open('GET', url, true);
        //    xmlhttp.onload = function () {
        //        ReactDOM.render(<Detail content={xmlhttp.responseText} paper={paper} searchid={searchid} />, document.getElementById("detail"+id));
        //        document.getElementById("h"+id).style.fontSize = '20px';
        //    }.bind(this);
        //    xmlhttp.send();
        //}
        if(!this.state.detail) {
            $('.modal').modal('toggle');
            console.info("Fetching detail.");
            xmlhttp.open('GET', url, true);
            xmlhttp.onload = function () {
                //ReactDOM.render(<Detail content={xmlhttp.responseText} paper={paper} searchid={searchid} />, document.getElementById("detail"+id));
                this.setState({selected: 'selected', detail: xmlhttp.responseText});
                $('.modal').modal('toggle');
            }.bind(this);
            xmlhttp.send();
        }
        else {
            if (this.state.selected) {
                this.setState({selected: ''});
                console.info("Hide.");
            }
            else {
                this.setState({selected: 'selected'});
                console.info("Show.");
            }
        }
    },
    render: function(){
        var searchid = this.props.searchid;
        var paper = this.props.paper;
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
        return(
            <li className={"list-group-item "+ this.state.selected}>
                <div className="div_title">
                <a href="#" onClick={this.showDetails}>
                    <span className="label label-dark title" id={"h"+paper["PMID"]}>{paper["Title"]}</span>
                </a>
                    </div>
                <div className="div_author">
                <span>
                    {
                        paper["Author"].split(", ").map(function(author, index){
                            var plus_concatenated = author.split(" ").join("+");
                            var url = "https://scholar.google.com/scholar?as_q=&as_epq=&as_oq=&as_eq=&as_occt=any&as_sauthors="+plus_concatenated+"&as_publication=&as_ylo=&as_yhi=&btnG=&hl=en&as_sdt=0%2C5";
                            return(
                                <span className="label label-default author" key={index}>
                                    <a target="_blank" href={url}>{author}</a>
                                </span>
                            );
                        })
                    }
                </span>
                    </div>
                <div className="metainfo">
                    <span className="label label-info journal"><a target="_blank" href={"http://google.com/search?btnI=1&q="+paper["Journal"]}>{ paper["Journal"] ? "Journal: " + paper["Journal"] : ""}</a></span>
                    <span className="label label-success pubdate">{ paper["PubDate"] ? "PubDate: " + paper["PubDate"] : ""}</span>
                    <span className="label label-warning score">{ paper["Score"] ? "Score: " + paper["Score"].toFixed(2) : ""}</span>
                    {citation_url}
                    <Detail content={this.state.detail} paper={paper} searchid={searchid} />
                </div>
            </li>
        );
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
                        papers.map(function (paper, index) {
                            return (
                                <Paper paper={paper} searchid={searchid} key={index} />
                            );
                        }, this)
                    }
                </ul>
                </div>
            );
        }
        else {
            return(
                <p>"No result."</p>
            );
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
                return(<li key={index} onClick={this.handleClick} data-id={item} className={(item == current ? "active" : "") + " " + (item > pages ? "disabled" : "")}><a>{item}</a></li>);
            }
            else {
                return(<li key={index} data-id={item} className={(item == current ? "active" : "") + " " + (item > pages ? "disabled" : "")}><a>{item}</a></li>);
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


//
//var waitingDialog = waitingDialog || (function ($) {
//    'use strict';
//
//    // Creating modal dialog's DOM
//    var $dialog = $(
//        '<div class="modal fade" data-backdrop="static" data-keyboard="false" tabindex="-1" role="dialog" aria-hidden="true" style="padding-top:15%; overflow-y:visible;">' +
//        '<div class="modal-dialog modal-m">' +
//        '<div class="modal-content">' +
//            '<div class="modal-header"><h3 style="margin:0;"></h3></div>' +
//            '<div class="modal-body">' +
//                '<div class="progress progress-striped active" style="margin-bottom:0;"><div class="progress-bar" style="width: 100%"></div></div>' +
//            '</div>' +
//        '</div></div></div>');
//
//    return {
//        /**
//         * Opens our dialog
//         * @param message Custom message
//         * @param options Custom options:
//         *                options.dialogSize - bootstrap postfix for dialog size, e.g. "sm", "m";
//         *                options.progressType - bootstrap postfix for progress bar type, e.g. "success", "warning".
//         */
//        show: function (message, options) {
//            // Assigning defaults
//            if (typeof options === 'undefined') {
//                options = {};
//            }
//            if (typeof message === 'undefined') {
//                message = 'Loading';
//            }
//            var settings = $.extend({
//                dialogSize: 'm',
//                progressType: '',
//                onHide: null // This callback runs after the dialog was hidden
//            }, options);
//
//            // Configuring dialog
//            $dialog.find('.modal-dialog').attr('class', 'modal-dialog').addClass('modal-' + settings.dialogSize);
//            $dialog.find('.progress-bar').attr('class', 'progress-bar');
//            if (settings.progressType) {
//                $dialog.find('.progress-bar').addClass('progress-bar-' + settings.progressType);
//            }
//            $dialog.find('h3').text(message);
//            // Adding callbacks
//            if (typeof settings.onHide === 'function') {
//                $dialog.off('hidden.bs.modal').on('hidden.bs.modal', function (e) {
//                    settings.onHide.call($dialog);
//                });
//            }
//            // Opening dialog
//            $dialog.modal();
//        },
//        /**
//         * Closes dialog
//         */
//        hide: function () {
//            $dialog.modal('hide');
//        }
//    };
//
//})(jQuery);

var WaitingDialog = React.createClass({
    render: function(){
        return(
            <div className="modal fade" data-backdrop="static" data-keyboard="false" tabIndex="-1" role="dialog" aria-hidden="true">
                <div className="modal-dialog modal-m">
                    <div className="modal-content">
                    <div className="modal-header"><h3>Loading</h3></div>
                    <div className="modal-body">
                    <div className="progress progress-striped active"><div className="progress-bar"></div></div>
                    </div></div></div></div>
        )
    }
});

ReactDOM.render(<App />, document.getElementById("form"));
ReactDOM.render(<WaitingDialog />, document.getElementById("waitingdialog"));