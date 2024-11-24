
% This is so that we can edit the sibling and parent statements in python
:- dynamic siblings/2.
:- dynamic parent/2.
:- dynamic sister/2.
:- dynamic female/1.



% Basically says X and Y are siblings if P is a parent to both X and y, and X and Y are not the same person
siblings(X, Y) :-
parent(P, X),
parent(P, Y),
X \= Y.

female(alice).
female(other_female_person).