import React from 'react';
import ReactDOM from 'react-dom';
import { Router, Route, IndexRoute, Link, hashHistory } from 'react-router';
import Subscription from './subscription';
import SearchApp from './search';

require("../css/main.scss");
require("../css/subscription.scss");
require("../css/search.scss");
require("../css/one-item.scss");

// var Controller = function(){
//     var keyword = '';
//     var page = 1;
//     var order_by = "Default";
//     var filter_by = "Default";

//     return{
//         loadData: function() {
//             $('.modal').modal('toggle');
//             var xmlhttp = new XMLHttpRequest();
//             xmlhttp.timeout = 300000;
//             var url = "/search/" + keyword + "?page=" + page + "&order_by=" + order_by + "&filter_by=" + filter_by;
//             xmlhttp.open("GET", url, true);
//             //r.onreadystatechange = function () {
//             xmlhttp.onload = function () {
//                 //if (xmlhttp.readyState != 4 || xmlhttp.status != 200) return;
//                 var j = JSON.parse(xmlhttp.responseText);
//                 console.info(j);
//                 //if(!j[0] || j[0].length == 0) {
//                 //    console.info("0 Results Received.")
//                 //}
//                 //var alert = ""
//                 //if (j[2] == 1) {
//                 //    alert = "Failed to fetch data from PubMed."
//                 //}
//                 //waitingDialog.hide();
//                 $('.modal').modal('hide');
//                 ReactDOM.render(<OutPut papers={j["result"]} pages={j["result_info"]["page"]} current={page} searchid={j["result_info"]["id"]} alert="" query={keyword} />, document.getElementById("result"));
//                 // ReactDOM.render(<span className="navbar-text">{j["result_info"]["count"] +" results found."}</span>, document.getElementById("span_num_results"));
//                 ReactDOM.render(<OrderBy />, document.getElementById("span_order_by"));
//                 ReactDOM.render(<Filter words={j["result_info"]["words"]} />, document.getElementById("filter_container"))
//             }.bind(this);
//             xmlhttp.ontimeout = function(){
//                 console.info("AJAX Timeout.");
//                 ReactDOM.render(<span>AJAX Timeout.</span>, document.getElementById("num_results"));
//                 $('.modal').modal('toggle');
//             };
//             xmlhttp.onerror = function () {
//                 console.info("AJAX Error.");
//                 ReactDOM.render(<span>AJAX Error.</span>, document.getElementById("num_results"));
//                 $('.modal').modal('toggle');
//             };
//             xmlhttp.send();
//         },
//         loadInitialData: function(p_keyword=keyword, p_page=1, p_order_by="Default", p_filter_by="Default") {
//             keyword = p_keyword;
//             page = p_page;
//             order_by = p_order_by;
//             filter_by = p_filter_by;
//             this.loadData();
//         },
//         loadNewPage: function(p) {
//             page = p;
//             console.info("loadNewPage:" + p);
//             this.loadData();
//         }
//     };
// }();



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

// class Detail extends React.Component {
//     render() {
//         console.log(this.props.show_detail);
//         if (this.props.show_detail) {
//             return (
//                 <div className="detail">
//                     <a href={"/jump/"}>
//                         {this.props.paper["Title"]}
//                     </a>
//                     <div className="abstract"
//                          dangerouslySetInnerHTML={{__html: this.props.paper["Abstract"].split(this.props.query).join("<span class=\"highlight\">" + this.props.query + "</span>")}}
//                     />
//                 </div>
//             )
//         }
//         else {
//             return null;
//         }
//     }
// }

// class Paper extends React.Component {
//     constructor() {
//         super();
//         this.state = {
//             selected: false
//         };
//         this.showDetails = this.showDetails.bind(this);
//     }

//     showDetails() {
//         console.log("showDetails");
//         this.setState({selected: !this.state.selected});
//     }

//     render(){
//         let paper = this.props.paper;

//         return(
//             <li className="list-group-item">
//                 <div className="one-item">
//                 <div className="div_title">
//                 <a href="javascript:void(0)" onClick={this.showDetails}>
//                     <span className="label label-dark title" id={"h"+paper["PMID"]}>{paper["Title"]}</span>
//                 </a>
//                     </div>
//                 <div className="div_author">
//                 <span>
//                     {
//                         paper["Authors"].map(function(author, index) {
//                             var plus_concatenated = author.split(" ").join("+");
//                             var url = "https://scholar.google.com/scholar?q=author%3A"+plus_concatenated+"&btnG=&hl=en&as_sdt=0%2C5";
//                             return(
//                                 <span className="label label-default author" key={index}>
//                                     <a target="_blank" href={url}>{author}</a>
//                                 </span>
//                             );
//                         })
//                     }
//                 </span>
//                     </div>
//                 <div className="metainfo">
//                     <span className="label label-info journal"><a target="_blank" href={"http://google.com/search?btnI=1&q="+paper["Journal"]}>{ paper["Journal"] ? "Journal: " + paper["Journal"] : "Journal: Unknown"}</a></span>
//                     <span className="label label-success pubdate">{ paper["Date"] ? "Date: " + paper["Date"] : "Year: Unknown"}</span>
//                     <span className="label label-warning score">{ paper["Score"] ? "Score: " + paper["Score"].toFixed(2) : ""}</span>
//                 </div>
//                 <Detail {...this.props} show_detail={this.state.selected} />
//                 </div>
//             </li>
//         );
//     }
// }



// var Pagination = React.createClass({
//     handleClick: function(event) {
//         Controller.loadNewPage(event.currentTarget.dataset.id);
//         console.info(event.currentTarget.dataset.id);
//     },
//     render: function() {
//         var pages = this.props.pages;
//         var current = this.props.current;
//         var display_from = current - 2;
//         if((pages <= 5) || (current < 3)) {
//             display_from = 1;
//         }
//         else if(display_from+4 > pages){
//             display_from = pages - 4;
//         }
//         var display_to = display_from + 4;
//         var arr = [];
//         while(display_from < display_to+1){
//             arr.push(display_from++);
//         }
//         var pageli = function(item, index){
//             if(item <= pages) {
//                 return(<li key={index} onClick={this.handleClick} data-id={item} className={(item == current ? "active" : "") + " " + (item > pages ? "disabled" : "")}><a>{item}</a></li>);
//             }
//             else {
//                 return(<li key={index} data-id={item} className={(item == current ? "active" : "") + " " + (item > pages ? "disabled" : "")}><a>{item}</a></li>);
//             }
//         }.bind(this);

//         if(pages > 0) {
//             return(
//                 <nav className="navbar navbar-default navbar-fixed-bottom">
//                     <div className="container mypagination">
//                         <nav>
//                             <ul className="pagination">
//                                 <li className={current==1 ? "disabled" : ""} onClick={this.handleClick} data-id={1}>
//                                     <a href="#" aria-label="Previous">
//                                         <span aria-hidden="true">&laquo;</span>
//                                     </a>
//                                 </li>
//                                 {
//                                     arr.map(pageli)
//                                 }
//                                 <li onClick={this.handleClick} data-id={pages}>
//                                     <a href="#" aria-label="Next">
//                                         <span aria-hidden="true">&raquo;</span>
//                                     </a>
//                                 </li>
//                             </ul>
//                         </nav>
//                     </div>
//                 </nav>
//             )
//         }
//         else {
//             return(
//                 <div></div>
//             )
//         }
//     }
// });



class Login extends React.Component {
    constructor(props) {
      super(props);
      this.state = {username: null};
    }

    componentWillMount() {
        var xmlhttp = new XMLHttpRequest();
        var url = "/checklogin";
        xmlhttp.open("GET", url, true);
        xmlhttp.onload = () => {
            var j = JSON.parse(xmlhttp.responseText);
            if(j.username) {
                this.setState({username: j.username, loaded: true});
            }
            else {
                this.setState({loaded: true});
            }
        };
        xmlhttp.send();
    }

    render(){
        if(this.state.loaded) {
            if(this.state.username) {
                return(
                    <div id='login'>
                        <p className="navbar-text">{this.state.username}</p>
                        <a href='/logout'><button className="btn btn-info navbar-btn">Logout</button></a>
                        { (this.props.routes[this.props.routes.length - 1].path=="/subscription")
                        ?<a href='/#/'><button className="btn btn-info navbar-btn l10">Homepage</button></a>
                        :<a href='/#/subscription'><button className="btn btn-info navbar-btn l10">Subscription</button></a>}
                    </div>
                )
            }
            else{
                return(
                    <div id='login'>
                        <a href='/register'><button className="btn btn-info navbar-btn" id="register_btn">Register</button></a>
                        <a href='/login'><button className="btn btn-info navbar-btn">Login</button></a>
                    </div>
                )
            }
        }
        else {
            return null;
        }
    }
}



class App extends React.Component {
    render() {
        return (
            <div>
            <nav className="navbar navbar-default navbar-fixed-top mynavbar">
                <div className="container">
                    <div className="row">
                        <div className="col-sm-8">
                        </div>
                        <div className="col-sm-4">
                            <div className="logincol">
                                <Login {...this.props} />
                            </div>
                        </div>
                    </div>
                </div>
            </nav>
            {this.props.children}
            </div>
        );
    }
}


var WaitingDialog = React.createClass({
    render: function(){
        return(
            <div className="modal fade" id="loading" data-backdrop="static" data-keyboard="false" tabIndex="-1" role="dialog" aria-hidden="true">
                <div className="modal-dialog modal-m">
                    <div className="modal-content">
                    <div className="modal-header"><h3>Loading</h3></div>
                    <div className="modal-body">
                    <div className="progress progress-striped active"><div className="progress-bar"></div></div>
                    </div></div></div></div>
        )
    }
});

ReactDOM.render((
  <Router history={hashHistory}>
    <Route path="/" component={App}>
        <IndexRoute component={SearchApp} />
        <Route path="/search/:keyword" component={SearchApp} />
        <Route path="/subscription" component={Subscription} />
    </Route>
  </Router>
), document.getElementById("main"));

// ReactDOM.render(<App />, document.getElementById("form"));
ReactDOM.render(<WaitingDialog />, document.getElementById("waitingdialog"));
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
