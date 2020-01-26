describe('All Users', () => {
    it('should display the all-users page correctly if the user is not logged in', () => {
        cy
            .visit('/all-users')
            .get('h1').contains('All Users')
            .get('.navbar-burger').click()
            .get('a').contains('All Users').should('not.be.visible')
            .get('a').contains('Log Out').should('not.be.visible')
            .get('a').contains('Register')
            .get('a').contains('Log In')
            .get('a').contains('Users')
            .get('.notification.is-success').should('not.be.visible');
    });
});