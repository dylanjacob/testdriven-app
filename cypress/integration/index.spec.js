describe('Index', () => {
    it('users should be able to view the "/" page', () => {
        cy
            .visit('/')
            .get('h1').contains('All Users')
            .get('thead > tr').children(0).contains('ID')
            .get('thead > tr').children(1).contains('Email')
            .get('thead > tr').children(2).contains('Username')
            .get('thead > tr').children(3).contains('Active')
            .get('thead > tr').children(4).contains('Admin');
    });
});