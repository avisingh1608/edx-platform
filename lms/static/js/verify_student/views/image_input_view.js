/**
 * Allow users to upload an image using a file input.
 *
 * This uses HTML Media Capture so that iOS will
 * allow users to use their camera instead of choosing
 * a file.
 */

 var edx = edx || {};

 (function( $, _, Backbone, gettext ) {
    'use strict';

    edx.verify_student = edx.verify_student || {};

    edx.verify_student.ImageInputView = Backbone.View.extend({

        template: "#image_input-tpl",

        initialize: function( obj ) {
            this.$submitButton = obj.submitButton || "";
            this.modelAttribute = obj.modelAttribute || "";
            this.errorModel = obj.errorModel || null;
        },

        render: function() {
            var renderedHtml = _.template( $( this.template ).html(), {} );
            $( this.el ).html( renderedHtml );

            this.$input = $( 'input.image-upload' );
            this.$preview = $( 'img.preview' );
            this.$input.on('change', _.bind( this.handleInputChange, this ) );

            return this;
        },

        handleInputChange: function( event ) {
            var files = event.target.files,
                reader = new FileReader();
            if ( files[0] && files[0].type.match( 'image.[png|jpg|jpeg]' ) ) {
                reader.onload = _.bind( this.handleImageUpload, this );
                reader.onerror = _.bind( this.handleUploadError, this );
                reader.readAsDataURL( files[0] );
            }
            else if ( files.length === 0 ) {
                this.handleUploadError( false );
            }
            else {
                this.handleUploadError( true );
            }
        },

        handleImageUpload: function( event ) {
            var imageData = event.target.result;
            this.model.set( this.modelAttribute, imageData );
            this.displayImage( imageData );
            this.setSubmitButtonEnabled( true );
            this.trigger( 'imageCaptured' );
        },

        displayImage: function( imageData ) {
            if ( imageData ) {
                this.$preview.attr( 'src', imageData );
            } else {
                this.$preview.attr( 'src', '' );
            }
        },

        handleUploadError: function( displayError ) {
            this.displayImage( null );
            this.setSubmitButtonEnabled( false );
            if ( this.errorModel ) {
                if ( displayError ) {
                    this.errorModel.set({
                        errorTitle: gettext( 'Image Upload Error' ),
                        errorMsg: gettext( 'Please verify that you have uploaded a valid image (PNG and JPEG).' ),
                        shown: true
                    });
                } else {
                    this.errorModel.set({
                        shown: false
                    });
                }
            }
        },

        setSubmitButtonEnabled: function( isEnabled ) {
            $( this.$submitButton )
                .toggleClass( 'is-disabled', !isEnabled )
                .prop( 'disabled', !isEnabled )
                .attr('aria-disabled', !isEnabled);
        }
    });

 })( jQuery, _, Backbone, gettext );
