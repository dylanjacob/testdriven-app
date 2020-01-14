import React from 'react';
import { shallow, mount } from 'enzyme';
import renderer from 'react-test-renderer';
import { MemoryRouter as Router } from 'react-router-dom';

import FormErrors from '../forms/FormErrors';
import { registerFormRules, loginFormRules } from "../forms/form-rules.js";

const registerFormProps = {
    formType: 'Register',
    formRules: registerFormRules
};

const loginFormProps = {
    formType: 'Login',
    formRules: loginFormRules
};

const testData = [
    registerFormProps,
    loginFormProps
];

describe('FormErrors', () => {
    testData.forEach((el) => {
        const component = <FormErrors {...el} />;
        it(`FormErrors (with ${el.formType} form) renders properly`, () => {
            const wrapper = shallow(component);
            const ul = wrapper.find('ul');
            expect(ul.length).toBe(1);
            const li = wrapper.find('li');
            expect(li.length).toBe(el.formRules.length);
            let i=0;
            el.formRules.forEach((rule) => {
                expect(li.get(i).props.children).toContain(rule.name);
                i=i+1;
            });
        });
        it(`FormErrors (with ${el.formType} form) renders a snapshot properly`, () => {
            const tree = renderer.create(<Router>component</Router>).toJSON();
            expect(tree).toMatchSnapshot();
        });
    });
});