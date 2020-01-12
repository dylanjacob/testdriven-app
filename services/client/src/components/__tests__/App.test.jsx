import React from 'react';
import { shallow } from 'enzyme';

import App from '../../App.jsx';

beforeAll(() => {
    global.localStorage = {
        getItem: () => 'someToken'
    };
});

test("App renders without crashing", () => {
    const wrapper = shallow(<App/>);
});