/* eslint no-magic-numbers: 0 */
import React, { useState } from 'react';

import { DangerouslySetInnerHtml } from '../lib';

const App = () => {

    const [state, setState] = useState({value:''});
    const setProps = (newProps) => {
            setState(newProps);
        };

    return (
        <div>
            <DangerouslySetInnerHtml
                setProps={setProps}
                {...state}
            />
        </div>
    )
};


export default App;
