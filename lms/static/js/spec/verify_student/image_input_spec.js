define([
    'jquery',
    'backbone',
    'js/common_helpers/template_helpers',
    'js/common_helpers/ajax_helpers',
    'js/verify_student/views/image_input_view',
    'js/verify_student/models/verification_model'
], function( $, Backbone, TemplateHelpers, AjaxHelpers, ImageInputView, VerificationModel ) {
    'use strict';

    describe( 'edx.verify_student.ImageInputView', function() {

        var createView = function() {
            return new ImageInputView({
                el: $( '#current-step-container' ),
                model: new VerificationModel({}),
                modelAttribute: 'faceImage',
                errorModel: new ( Backbone.Model.extend({}) )(),
                submitButton: $( '#submit_button' ),
            }).render();
        };

        var uploadImage = function( view, fileType ) {
            // TODO

        };

        var expectPreview = function( view, fileType ) {
            // TODO

        };

        var expectSubmitEnabled = function( isEnabled ) {
            // TODO

        };

        var expectImageData = function( view, hasData ) {
            // TODO

        };

        var expectError = function( view ) {
            // TODO

        };

        beforeEach(function() {
            setFixtures(
                '<div id="current-step-container"></div>' +
                '<input type="button" id="submit_button"></input>'
            );
            TemplateHelpers.installTemplate( 'templates/verify_student/image_input' );
        });

        it( 'displays a preview of the uploaded image', function() {
            var view = createView();

            // Initially submit is disabled
            expectSubmitEnabled( false );

            // PNG upload
            uploadImage( view, 'png' );
            expectPreview( view, 'png' );
            expectSubmitEnabled( true );
            expectImageData( true );

            // JPEG upload
            uploadImage( view, 'jpeg' );
            expectPreview( view, 'jpeg' );
            expectSubmitEnabled( true );
            expectImageData( true );

            // Cancelled upload
            uploadImage( view, null );
            expectPreview( view, null );
            expectSubmitEnabled( false );
            expectImageData( false );
        });

        it( 'shows an error if the file type is not supported', function() {
            var view = createView();

            uploadImage( view, 'txt' );
            expectPreview( view, null );
            expectError( view );
            expectSubmitEnabled( false );
            expectImageData( view, false );
        });
    });
});
