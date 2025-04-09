import { SubscriptionLike, TeardownLogic } from './types';
/**
 * Represents a disposable resource, such as the execution of an Observable. A
 * Subscription has one important method, `unsubscribe`, that takes no argument
 * and just disposes the resource held by the subscription.
 *
 * Additionally, subscriptions may be grouped together through the `add()`
 * method, which will attach a child Subscription to the current Subscription.
 * When a Subscription is unsubscribed, all its children (and its grandchildren)
 * will be unsubscribed as well.
 *
 * @class Subscription
 */
export declare class Subscription implements SubscriptionLike {
    private initialTeardown?;
    /** @nocollapse */
    static EMPTY: Subscription;
    /**
     * A flag to indicate whether this Subscription has already been unsubscribed.
     */
    closed: boolean;
    private _parentage;
    /**
     * The list of registered teardowns to execute upon unsubscription. Adding and removing from this
     * list occurs in the {@link #add} and {@link #remove} methods.
     */
    private _teardowns;
    /**
     * @param initialTeardown A function executed first as part of the teardown
     * process that is kicked off when {@link #unsubscribe} is called.
     */
    constructor(initialTeardown?: (() => void) | undefined);
    /**
     * Disposes the resources held by the subscription. May, for instance, cancel
     * an ongoing Observable execution or cancel any other type of work that
     * started when the Subscription was created.
     * @return {void}
     */
    unsubscribe(): void;
    /**
     * Adds a teardown to this subscription, so that teardown will be unsubscribed/called
     * when this subscription is unsubscribed. If this subscription is already {@link #closed},
     * because it has already been unsubscribed, then whatever teardown is passed to it
     * will automatically be executed (unless the teardown itself is also a closed subscription).
     *
     * Closed Subscriptions cannot be added as teardowns to any subscription. Adding a closed
     * subscription to a any subscription will result in no operation. (A noop).
     *
     * Adding a subscription to itself, or adding `null` or `undefined` will not perform any
     * operation at all. (A noop).
     *
     * `Subscription` instances that are added to this instance will automatically remove themselves
     * if they are unsubscribed. Functions and {@link Unsubscribable} objects that you wish to remove
     * will need to be removed manually with {@link #remove}
     *
     * @param teardown The teardown logic to add to this subscription.
     */
    add(teardown: TeardownLogic): void;
    /**
     * Checks to see if a this subscription already has a particular parent.
     * This will signal that this subscription has already been added to the parent in question.
     * @param parent the parent to check for
     */
    private _hasParent;
    /**
     * Adds a parent to this subscription so it can be removed from the parent if it
     * unsubscribes on it's own.
     *
     * NOTE: THIS ASSUMES THAT {@link _hasParent} HAS ALREADY BEEN CHECKED.
     * @param parent The parent subscription to add
     */
    private _addParent;
    /**
     * Called on a child when it is removed via {@link #remove}.
     * @param parent The parent to remove
     */
    private _removeParent;
    /**
     * Removes a teardown from this subscription that was previously added with the {@link #add} method.
     *
     * Note that `Subscription` instances, when unsubscribed, will automatically remove themselves
     * from every other `Subscription` they have been added to. This means that using the `remove` method
     * is not a common thing and should be used thoughtfully.
     *
     * If you add the same teardown instance of a function or an unsubscribable object to a `Subcription` instance
     * more than once, you will need to call `remove` the same number of times to remove all instances.
     *
     * All teardown instances are removed to free up memory upon unsubscription.
     *
     * @param teardown The teardown to remove from this subscription
     */
    remove(teardown: Exclude<TeardownLogic, void>): void;
}
export declare const EMPTY_SUBSCRIPTION: Subscription;
export declare function isSubscription(value: any): value is Subscription;
//# sourceMappingURL=Subscription.d.ts.map