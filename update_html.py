import re

with open("blockwise-v2_1.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Mock DB
content = content.replace("const DB = {", "let DB = null; const DB_mock = {")

# 2. Join
old_join = """        function join(oid) {
            DB.rsvps.push({ id: nid("r"), outing_id: oid, user_id: ME, state: "rsvp" });
            credit(ME, -1, "Joined " + place(outing(oid).place_id).name, oid);
            render(); pulse();
            toast("You are in. 1 credit spent.");
        }"""
new_join = """        async function join(oid) {
            try {
                const res = await fetch(`/api/outings/${oid}/rsvp`, {
                    method: "POST", headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({ user_id: ME, state: "rsvp" })
                });
                if(!res.ok) throw new Error();
                await refreshDatabaseState();
                pulse();
                toast("You are in. 1 credit spent.");
            } catch(e) { toast("Error joining"); }
        }"""
content = content.replace(old_join, new_join)

# 3. Confirm Attendance
old_confirm = """        function confirmAttendance(oid) {
            const open = DB.rsvps.filter(r => r.outing_id === oid && r.state === "rsvp");
            let earned = 0;
            open.forEach(r => {
                const s = staged[r.id];
                if (!s) return;
                r.state = s;
                if (s === "attended") { credit(ME, +1, "Hosted " + user(r.user_id).username, oid); earned++; }
                delete staged[r.id];
            });
            render();
            if (earned) { pulse(); toast(`Confirmed. +${earned} credits`); }
            else toast("Confirmed. No credits earned.");
        }"""
new_confirm = """        async function confirmAttendance(oid) {
            const open = DB.rsvps.filter(r => r.outing_id === oid && r.state === "rsvp");
            let updates = [];
            open.forEach(r => {
                const s = staged[r.id];
                if (!s) return;
                updates.push({ user_id: r.user_id, status: s });
                delete staged[r.id];
            });
            try {
                await fetch(`/api/outings/${oid}/attendance`, {
                    method: "POST", headers: {"Content-Type": "application/json"},
                    body: JSON.stringify(updates)
                });
                await refreshDatabaseState();
                pulse(); toast(`Confirmed.`);
            } catch(e) { toast("Error confirming"); }
        }"""
content = content.replace(old_confirm, new_confirm)

# 4. f-go
old_fgo = """                DB.outings.unshift(o);
                go({ name: "tag", tag: o.tags[0] });
                toast("Posted. It's live on #" + o.tags[0]);"""
new_fgo = """                fetch("/api/outings", {
                    method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(o)
                }).then(() => refreshDatabaseState()).then(() => {
                    go({ name: "tag", tag: o.tags[0] });
                    toast("Posted. It's live on #" + o.tags[0]);
                });"""
content = content.replace(old_fgo, new_fgo)

# 5. render() at the end
old_render = """        view = fromHash(location.hash);
        render();
    </script>"""
new_render = """        view = fromHash(location.hash);
        
        async function refreshDatabaseState() {
            try {
                const res = await fetch("http://127.0.0.1:8000/api/state");
                if (!res.ok) throw new Error("Network error");
                DB = await res.json();
                render();
            } catch (err) {
                console.error("Failed to fetch state:", err);
                toast("Could not connect to backend.");
            }
        }

        refreshDatabaseState();
    </script>"""
content = content.replace(old_render, new_render)

with open("blockwise-v2_1.html", "w", encoding="utf-8") as f:
    f.write(content)

print("HTML file updated.")
