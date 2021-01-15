<h1>TXT</h1>

<section>
<h3>Discord Bot, made for fun, and for a dispute</h3>
<p>What Can This Bot:</p>
<ul>
    <li>Just Exists</li>
    <li>Support CRUD operations for files</li>
    <li>And get memes</li>
</ul>
<p>And forget all saied with me, nothing there not realized, YET</p>
</section>

<h3>Clone</h3>
<p>Firstly create virtual envorion</p>
<p>Second, In this dir, run this <code>pip install -r requirements.txt</code></p>
<p>You need to install postgresql and run this commands</p>
<code>
CREATE TABLE users(
id serial PRIMARY KEY, 
user_id bigint, 
name varchar(255), 
current_file varchar(255), 
user_path varchar(255), 
is_owner boolean); 
</code>
<p>and for guild table:</p> 
<code>
CREATE TABLE guilds(
id serial PRIMARY KEY, 
guild_id bigint, 
guild_name varchar(255));
</code>
<p>Almost Complete, just change values in "data.toml"</p>
<p>And Run with this command python bot.py</p>
