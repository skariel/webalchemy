/*   watching objects for changes so we can hook some functions.
 *   Taken from: https://gist.github.com/XoseLluis/4750176
 */
if (!Object.prototype.watch) {
	Object.prototype.watch = function(prop, handler){
		var desc = Object.getOwnPropertyDescriptor(this, prop);
		var newGet;
		var newSet;
		//these cases make little sense, so do nothing we won't be watching readonly descriptors
		if (!desc.configurable
		    || (desc.value === undefined && !desc.set)
			|| desc.writable === false)
			return;

		if (desc.value){
			var val = desc.value;
			newGet = function(){
				return val;
			};
			newSet = function(newVal){
				val = handler.call(this, prop, val, newVal);
			};
			//let's leverage the setter to store initial information to enable "unwatch"
			newSet._watchHelper = {
				initialType: "dataDescriptor"
			};
		}
		else{
			newGet = desc.get;
			newSet = function(newVal){
				val = handler.call(this, prop, val, newVal);
				desc.set.call(this, val);
			};
			newSet._watchHelper = {
				initialType: "accessorDescriptor",
				oldDesc: desc
			};
		}
		Object.defineProperty(this, prop, {
			get: newGet,
			set: newSet,
			configurable: true,
			enumerable: desc.enumerable
		});
	};

	Object.prototype.unwatch = function(prop){
		var desc = Object.getOwnPropertyDescriptor(this, prop);
		if (desc.set._watchHelper){
			if(desc.set._watchHelper.initialType == "dataDescriptor"){
				Object.defineProperty(this, prop, {
					value: this[prop],
					enumerable: desc.enumerable,
					configurable: true,
					writable: true
				});
			}
			else{
				Object.defineProperty(this, prop, {
					get: desc.get,
					set: desc.set._watchHelper.oldDesc.set,
					enumerable: desc.enumerable,
					configurable: true
				});
			}
		}
	};
}
