/*
	Angular controller for all the create_fields page logic
*/

var createFieldsApp = angular.module("createFieldsApp", ['ngResource']);

createFieldsApp.controller("CreateFieldsController", function($scope, $http, $q) 
{

    // On initation of controller
    $scope.init = function(job_id)
    {
        // Job ID passed through from view
        $scope.job_id = job_id;

        // Empty arrays for layouts and profiles
        $scope.layouts = [];
        $scope.profiles = [];

        // Get list of profiles for the page
        $http(
        {
            method: 'GET',
            url: '/get_profiles/' + $scope.job_id + '/',
            headers: {
                'Content-Type': 'application/json'
            }
        }).
        success(function(data, status) 
        {
            // Loop through resulting array
            for (var i = 0; i < data.length; i++)
            {
                // Create a new layout
                profile = {
                    'id': data[i].id,
                    'name': data[i].name,
                    'fullName': data[i].fullName,
                    'read': true,
                    'edit': true
                };

                $scope.profiles.push(profile);
            }
        }).
        error(function(data, status) {});

        // Initial settings for each row
        $scope.fields = [
            {   
                label: '',
                name: '',
                type: 'Text',
                length: '255',
                precision: '16',
                description: '',
                helptext: '',
                default: '',
                vislines: '5',
                decimal: '2',
                required: false,
                uniqueSetting: false,
                external: false,
                geodisplay: 'degrees',
                masktype: 'all',
                maskchar: 'asterisk',
                picklistvalues: '',
                sortalpha: false,
                firstvaluedefault: false,
                checkboxdefault: 'unchecked',
                uniquetype: 'insensitive',
                layouts_checkall: true,
                profiles_checkall_read: true,
                profiles_checkall_edit: true,
                layouts: [],
                profiles: $scope.profiles,
                deployStatus: 'info',
                deployMessage: 'Not Started',
            }
        ];

        // Set initial current field
        $scope.current_field = $scope.fields[0];

    };

    // Clear all rows
    $scope.clearAll = function()
    {
        $scope.fields = [];
        $scope.addRow();
    }

    // On change of the ojbect
    $scope.objectChange = function()
    {
        if ($scope.objectName === '')
        {
            $('#fields_table').hide('slow');
            $('#add_row').hide('slow');
            $('#deploy').hide('slow');
            $('#fields_table_info').show('slow');
        }
        else   
        {
            // Show table and hide message
            $('#fields_table').show('slow');
            $('#add_row').show('slow');
            $('#deploy').show('slow');
            $('#fields_table_info').hide('slow');


            /* Commenting out layout callout
            $('#progressModal .modal-header').html('<h4 class="modal-title">Finding layouts.</h4>');
            $('#progressModal .modal-body').html('<div>Querying for layouts for object...</div><div class="progress"><div class="progress-bar progress-bar-warning progress-bar-striped active" role="progressbar" aria-valuenow="100" aria-valuemin="0" aria-valuemax="100" style="width: 100%"></div></div></div>');
            $('#progressModal .modal-footer').html('');
            $('#progressModal').modal();

            // Make callout to retrieve layouts
            $http(
            {
                method: 'GET',
                url: '/get_layouts/' + $scope.job_id + '/' + $scope.objectName,
                headers: {
                    'Content-Type': 'application/json'
                }
            }).
            success(function(data, status) 
            {
                if (data.errorCode) 
                {
                    $('#progressModal .modal-header').html('<button type="button" class="close" data-dismiss="modal"><span aria-hidden="true">&times;</span><span class="sr-only">Close</span></button><h4 class="modal-title">Error</h4>');
                    $('#progressModal .modal-body').html('<div class="alert alert-danger" role="alert">There was an error querying for layouts: ' + data.errorCode + ' - ' + data.message + '</div>');
                    $('#progressModal .modal-footer').html('<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>');
                }
                else
                {   
                    // Loop through resulting array
                    for (var i = 0; i < data.length; i++)
                    {
                        // Create a new layout
                        $scope.layout = {
                            'name': data[i].name,
                            'checked': true
                        };

                        // Push to array
                        $scope.layouts.push($scope.layout);
                    }

                    // Set the layouts for the field
                    $scope.fields[0].layouts = $scope.layouts;

                    // Show table and hide message
                    $('#fields_table').show('slow');
                    $('#add_row').show('slow');
                    $('#deploy').show('slow');
                    $('#fields_table_info').hide('slow');

                    // Close the modal
                    $('#progressModal').modal('hide');

                }   

            }).
            error(function(data, status) 
            {
                $('#progressModal .modal-header').html('<button type="button" class="close" data-dismiss="modal"><span aria-hidden="true">&times;</span><span class="sr-only">Close</span></button><h4 class="modal-title">Error</h4>');
                $('#progressModal .modal-body').html('<div class="alert alert-danger" role="alert">There was an error querying for your layouts: ' + data.error + '</div>');
                $('#progressModal .modal-footer').html('<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>');
            });

            */
        }

    };

    // When field label changes
    $scope.labelChange = function(field)
    {
        var field_label = field.label;

        if ( field_label !== '' && field.name === '' )
        {
            // Remove non-alpha characters
            var field_name = field_label.replace(/[^a-zA-Z0-9 :]/g, '');

            // Remove all multiple spaces to a single space
            field_name = field_name.replace(/\s{2,}/g, ' ');

            // Replace spaces with _
            field_name = field_name.replace(/\s/g, '_');

            // If starts with number, replace with X
            if ( !isNaN(field_name.charAt(0)) )
            {
                // Remove first character and add X
                field_name = 'X' + field_name.substring(1);
            }

            // Append __c
            field_name += '__c';
            
            // Put into Field Name input
           field.name = field_name;
        }
    };

    $scope.typeChange = function(field)
    {
        var field_type = field.type;

        // If long text or rich text, update the field length
        if (field_type == 'LongTextArea' || field_type == 'Html') {

            // Set to the max length
            field.length = '131072';
        }
        else {
            // Else default back to 255
            field.length = '255';
        }
    };

    // Add row function
	$scope.addRow = function()
	{		
		$scope.fields.push(
		{ 
			label: '',
        	name: '',
        	type: 'Text',
        	length: '255',
            precision: '16',
        	description: '',
        	helptext: '',
        	default: '',
        	vislines: '5',
        	decimal: '2',
        	required: false,
        	uniqueSetting: false,
        	external: false,
        	geodisplay: 'degrees',
        	masktype: 'all',
        	maskchar: 'asterisk',
        	picklistvalues: '',
        	sortalpha: false,
        	firstvaluedefault: false,
        	checkboxdefault: 'unchecked',
            uniquetype: 'insensitive',
            deployStatus: 'info',
            deployMessage: 'Not Started',
            layouts_checkall: true,
            profiles: angular.copy($scope.profiles),
            profiles_checkall_read: true,
            profiles_checkall_edit: true,
		});
	};

	// Delete a row function
	$scope.removeRow = function(index)
	{
		$scope.fields.splice(index, 1);		
	};

	// Called when the Edit button is clicked for field options
	$scope.editRow = function(field)
	{
        // Hide all field options
        $('#fieldOptionModal .field_options').hide();

        // Display the appropriate field options for field type
        $('.' + field.type + '_options').show();

		// Set the current field on the form. This is used for when we need to save values back to the field
		$scope.current_field = field;

		// Copy existing values to the form
		$scope.length 				     = field.length;
    	$scope.description 			     = field.description;
    	$scope.helptext 			     = field.helptext;
    	$scope.default 				     = field.default;	
    	$scope.vislines 			     = field.vislines;
    	$scope.decimal 				     = field.decimal;
    	$scope.required 			     = field.required;
    	$scope.uniqueSetting 		     = field.uniqueSetting;
    	$scope.external 			     = field.external;
    	$scope.geodisplay 			     = field.geodisplay;
    	$scope.masktype 			     = field.masktype;
    	$scope.maskchar 			     = field.maskchar;
    	$scope.picklistvalues 		     = field.picklistvalues;
    	$scope.sortalpha	 		     = field.sortalpha;
    	$scope.firstvaluedefault 	     = field.firstvaluedefault;
    	$scope.checkboxdefault 		     = field.checkboxdefault;
        $scope.uniquetype                = field.uniquetype;
        $scope.precision                 = field.precision;

         // load modal
        $('#fieldOptionModal').modal();
	};

	// Called when the user clicks save
	$scope.saveRow = function()
	{
		// Determine what field to update
		var field = $scope.current_field;

		// Copy form values to field
		field.length 				    = $scope.length;
    	field.description 			    = $scope.description;
    	field.helptext 				    = $scope.helptext;
    	field.default 				    = $scope.default;	
    	field.vislines 				    = $scope.vislines;
    	field.decimal 				    = $scope.decimal;
    	field.required 				    = $scope.required;
    	field.uniqueSetting 		    = $scope.uniqueSetting;
    	field.external 				    = $scope.external;
    	field.geodisplay 			    = $scope.geodisplay;
    	field.masktype 				    = $scope.masktype;
    	field.maskchar 				    = $scope.maskchar;
    	field.picklistvalues 		    = $scope.picklistvalues;
    	field.sortalpha	 			    = $scope.sortalpha;
    	field.firstvaluedefault 	    = $scope.firstvaluedefault;
    	field.checkboxdefault 		    = $scope.checkboxdefault;
        field.uniquetype                = $scope.uniquetype;
        field.precision                 = $scope.precision;
	};

    // When edit on profiles is selected.
    $scope.editProfiles = function(field)
    {
        // Set current field
        $scope.current_field = field;

        // Set options for modal
        $scope.profiles_checkall_read    = field.profiles_checkall_read;
        $scope.profiles_checkall_edit    = field.profiles_checkall_edit;
        $scope.profiles                  = angular.copy(field.profiles);

        // Load modal
        $('#profileModal').modal();
    };

    // On click on the save to all function
    $scope.saveRowProfiles = function()
    {
        // Set field to new settings
        $scope.current_field.profiles_checkall_read    = $scope.profiles_checkall_read;
        $scope.current_field.profiles_checkall_edit    = $scope.profiles_checkall_edit;
        $scope.current_field.profiles                  = angular.copy($scope.profiles);
    };

    // On click on the save to all function
    $scope.saveRowToAllProfiles = function()
    {
        // Apply current settings to all fields
        for (var i = 0; i < $scope.fields.length; i++)
        {
            $scope.fields[i].profiles_checkall_read   = $scope.profiles_checkall_read;
            $scope.fields[i].profiles_checkall_edit   = $scope.profiles_checkall_edit;
            $scope.fields[i].profiles                 = angular.copy($scope.profiles);
        }    
    };

    // When checkall on read is click
    $scope.checkAllRead = function()
    {
        // Check all read checkboxes
        if ($scope.profiles_checkall_read)
        {
            for (var i = 0; i < $scope.profiles.length; i++)
            {
                $scope.profiles[i].read = true;
            }
        }
        else
        {
            // Otherwise uncheck all read and edit boxes
            for (var i = 0; i < $scope.profiles.length; i++)
            {
                $scope.profiles[i].read = false;
                $scope.profiles[i].edit = false;
            }
            $scope.profiles_checkall_edit = false;
        }
    };

    // When checkall on edit is click
    $scope.checkAllEdit = function()
    {
        // check all edit when edit all is checked
        if ($scope.profiles_checkall_edit)
        {
            for (var i = 0; i < $scope.profiles.length; i++)
            {
                $scope.profiles[i].edit = true;

                // If read isn't checked, we need to check it too
                if (!$scope.profiles[i].read)
                {
                    $scope.profiles[i].read = true;
                }
            }
            // If Edit all is checked - read should be checked.
            $scope.profiles_checkall_read = true;
        }
        else
        {
            // Otherwise uncheck all edit
            for (var i = 0; i < $scope.profiles.length; i++)
            {
                $scope.profiles[i].edit = false;
            }
        }
    };

    // When the read checkbox is changed
    $scope.readChange = function(profile)
    {
        // If read is disabled - edit needs to be disabled
        if (!profile.read)
        {
            profile.edit = false;
        }
    };

    // When the read checkbox is changed
    $scope.editChange = function(profile)
    {
        // If edit is enabled and read isn't enabled - read needs to be enabled
        if (profile.edit && !profile.read) 
        {
            profile.read = true;
        }
    };

    // On click of deploy. Send all data to the controller for deployment to Salesforce.
    $scope.deploy = function()
    {
        $('#deployModal .modal-header').html('');
        $('#deployModal .modal-footer').html('');
        $('#deployModal').modal();

        // Array of fields that require profile updates
        fields_for_profile_update = [];

        $scope.requests = [];

        angular.forEach($scope.fields,function(field, index)
        {
            if (field.name !== '' && field.label !== '')
            {
                field.deployStatus = 'warning';
                field.deployMessage = 'Deploying field...';

                // Add request to a list
                $scope.requests.push(
                    $http(
                    {
                        method: 'POST',
                        url: '/deploy_field/' + $scope.job_id + '/' + $scope.objectName + '/',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken')
                        },
                        data: field
                    }).
                    success(function(data, status) 
                    {
                        if (data.success)
                        {
                            field.deployStatus = 'success';
                            field.deployMessage = 'Field successfully created.';

                            fields_for_profile_update.push(field);
                        }
                        else
                        {
                            field.deployStatus = 'danger';
                            field.deployMessage = data[0].errorCode + ' - ' + data[0].message;
                        }
                    }).
                    error(function(data, status) 
                    {
                        field.deployStatus = 'danger';
                        field.deployMessage = data;
                    })
                );
            }
            else
            {
                field.deployStatus = 'danger';
                field.deployMessage = 'Label and Name required to deploy.';
            }

        });

        if ($scope.requests.length)
        {
            // Execute requests
            $q.all($scope.requests).then(function() 
            {

                // If there are profiles to deploy, let's deploy them
                if (fields_for_profile_update.length)
                {

                    $http({
                        method: 'POST',
                        url: '/deploy_profiles/' + $scope.job_id + '/' + $scope.objectName + '/',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken')
                        },
                        data: fields_for_profile_update
                    }).
                    success(function(data, status){
                        //console.log(data);
                    }). 
                    error(function(data, status){
                        //console.log(data);
                    }); 
                }

                $('#deployModal .modal-header').html('<button type="button" class="close" data-dismiss="modal"><span aria-hidden="true">&times;</span><span class="sr-only">Close</span></button><h4 class="modal-title">Deploying Fields...</h4>');
                $('#deployModal .modal-footer').html('<button type="button" class="btn btn-md" data-dismiss="modal">Close</button>');

            });
        }
        else
        {
            $('#deployModal .modal-header').html('<button type="button" class="close" data-dismiss="modal"><span aria-hidden="true">&times;</span><span class="sr-only">Close</span></button><h4 class="modal-title">Deploying Fields...</h4>');
            $('#deployModal .modal-footer').html('<button type="button" class="btn btn-md" data-dismiss="modal">Close</button>');
        }

    };

});