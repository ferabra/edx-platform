/**
 * The EditXBlockModal is a Backbone view that shows an xblock editor in a modal window.
 * It is invoked using the edit method which is passed an existing rendered xblock,
 * and upon save an optional refresh function can be invoked to update the display.
 */
define(["jquery", "underscore", "gettext", "js/views/modals/base_modal", "js/views/utils/view_utils",
    "js/models/xblock_info", "js/views/xblock_editor", "date",
    "js/collections/course_grader", "js/views/overview_assignment_grader"],
    function($, _, gettext, BaseModal, ViewUtils, XBlockInfo, XBlockEditorView, date, CourseGraderCollection, OverviewAssignmentGrader) {
        var EditSectionXBlockModal = BaseModal.extend({
            events : {
                "click .action-save": "save",
                "click .action-modes a": "changeMode"
            },

            options: $.extend({}, BaseModal.prototype.options, {
                modalName: 'edit-xblock',
                addSaveButton: true
            }),

            initialize: function(xblockInfo) {
                BaseModal.prototype.initialize.call(this);
                this.events = _.extend({}, BaseModal.prototype.events, this.events);
                this.template = this.loadTemplate('edit-section-xblock-modal');
                this.xblockInfo = xblockInfo;
                this.date = date;
                this.graderTypes = new CourseGraderCollection(JSON.parse(xblockInfo.get('course_graders')), {parse:true});
                this.SelectGraderView = OverviewAssignmentGrader.extend({
                   selectGradeType : function(e) {
                      e.preventDefault();
                      this.removeMenu(e);
                      this.assignmentGrade.set('graderType', ($(e.target).hasClass('gradable-status-notgraded')) ? 'notgraded' : $(e.target).text());
                      this.render();
                    }
                })
            },


            getDateTime: function(datetime) {
                var formatted_date, formatted_time;

                formatted_date = this.date.parse(datetime.split(' at ')[0]).toString('mm/dd/yy');
                formatted_time = this.date.parse(datetime.split(' at ')[1].split('UTC')[0]).toString('hh:mm');

                return {
                    'date': formatted_date,
                    'time': formatted_time,
                }
            },


            getContentHtml: function() {
                return this.template({
                    xblockInfo: this.xblockInfo,
                    getDateTime: this.getDateTime,
                    date: this.date,
                });
            },


            render: function() {
                BaseModal.prototype.render.call(this);
                this.$el.find('.date').datepicker({'dateFormat': 'm/d/yy'});
                this.$el.find('.time').timepicker({'timeFormat' : 'H:i'});
                new this.SelectGraderView({
                    el : this.$el.find('.gradable-status'),
                    graders : this.graderTypes,
                    hideSymbol : true,
                 });
            }



            // save: function(event) {
            //     var self = this,
            //         editorView = this.editorView,
            //         xblockInfo = this.xblockInfo,
            //         data = editorView.getXModuleData();
            //     event.preventDefault();
            //     if (data) {
            //         ViewUtils.runOperationShowingMessage(gettext('Saving&hellip;'),
            //             function() {
            //                 return xblockInfo.save(data);
            //             }).done(function() {
            //                 self.onSave();
            //             });
            //     }
            // },

        });

        return EditSectionXBlockModal;
    });
