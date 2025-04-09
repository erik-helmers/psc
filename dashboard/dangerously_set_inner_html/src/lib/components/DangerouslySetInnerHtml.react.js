import React, { useState } from 'react';
import PropTypes from 'prop-types';

/**
 * ExampleComponent is an example component.
 * It renders an input with the property `value`
 * which is editable by the user.
 */
const DangerouslySetInnerHtml = (props) => {
    const {id, value} = props;

    return (
        <div id={id}
            dangerouslySetInnerHTML={{__html: value}}/>
    );
}


DangerouslySetInnerHtml.propTypes = {
    /**
     * The ID used to identify this component in Dash callbacks.
     */
    id: PropTypes.string,

    /**
     * The html content of the div.
     */
    value: PropTypes.string,

    /**
     * Dash-assigned callback that should be called to report property changes
     * to Dash, to make them available for callbacks.
     */
    setProps: PropTypes.func
};

export default DangerouslySetInnerHtml;
